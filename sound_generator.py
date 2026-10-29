
from io import BytesIO
import wave

import numpy as np

SAMPLE_RATE = 22050
NOTE_DURATION = 1.2
SCALE_STEPS = [0, 2, 4, 5, 7, 9, 11, 12]


def make_tone(frequency, duration, brightness):
    """Create a soft musical tone with harmonics."""
    count = int(SAMPLE_RATE * duration)
    t = np.arange(count) / SAMPLE_RATE

    fundamental = np.sin(2 * np.pi * frequency * t)
    harmonic = np.sin(2 * np.pi * frequency * 2 * t)
    third = np.sin(2 * np.pi * frequency * 3 * t)

    tone = (
        fundamental
        + brightness * 0.28 * harmonic
        + brightness * 0.12 * third
    )

    # Smooth attack and release to avoid clicks.
    attack = np.minimum(1.0, t / 0.12)
    release = np.minimum(1.0, (duration - t) / 0.35)
    envelope = np.maximum(0.0, np.minimum(attack, release))

    return tone * envelope


def map_image_to_notes(features):
    """Map eight image regions to musical frequencies."""
    hue = features["hue"]
    brightness = features["brightness"]

    # Choose a tonal center from the overall hue.
    root_midi = 48 + int(hue * 12)

    # Brighter images use a slightly higher register.
    if brightness > 0.65:
        root_midi += 12

    notes = []

    for r, g, b in features["region_colors"]:
        # Region brightness determines scale position.
        region_brightness = max(r, g, b) / 255.0

        index = min(7, int(region_brightness * 8))
        semitone = SCALE_STEPS[index]

        midi_note = root_midi + semitone
        frequency = 440.0 * (2 ** ((midi_note - 69) / 12))

        notes.append({
            "midi": midi_note,
            "frequency": round(frequency, 2),
            "color": (r, g, b),
        })

    return notes


def generate_sound(features):
    """Synthesize an ambient melody from image features."""
    notes = map_image_to_notes(features)

    total_duration = len(notes) * NOTE_DURATION + 0.8
    total_samples = int(total_duration * SAMPLE_RATE)
    audio = np.zeros(total_samples, dtype=np.float64)

    saturation = features["saturation"]

    # Create a sequence of eight notes.
    for i, note in enumerate(notes):
        start = int(i * NOTE_DURATION * SAMPLE_RATE)

        tone = make_tone(
            note["frequency"],
            NOTE_DURATION * 1.5,
            saturation,
        )

        end = min(start + len(tone), total_samples)
        audio[start:end] += 0.34 * tone[:end - start]

    # Add a soft sustained harmonic background.
    root = notes[0]["frequency"]
    t = np.arange(total_samples) / SAMPLE_RATE

    background = (
        np.sin(2 * np.pi * (root / 2) * t)
        + 0.5 * np.sin(2 * np.pi * (root * 0.75) * t)
    )

    fade = np.minimum(1.0, t / 0.7)
    fade *= np.minimum(1.0, (total_duration - t) / 1.0)
    audio += 0.12 * background * np.maximum(0.0, fade)

    # Normalize to avoid clipping.
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.82

    pcm = (audio * 32767).astype("<i2")

    buffer = BytesIO()

    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())

    return buffer.getvalue(), notes
