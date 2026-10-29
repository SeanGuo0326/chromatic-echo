
from io import BytesIO
import wave

import numpy as np

SAMPLE_RATE = 22050
DURATION = 18.0

MOODS = {
    "Echo": "Spacious echoes and fading colour traces",
    "Flow": "Soft, continuously evolving sound materials",
    "Pulse": "Experimental rhythmic colour particles",
}

# Artistic timbre identities, not scientific colour frequencies.
MATERIALS = [
    "Warm Resonance",  # Red
    "Soft Bells",      # Orange
    "Golden Chimes",   # Yellow
    "Organic Waves",   # Green
    "Air and Glass",   # Cyan
    "Deep Water",      # Blue
    "Crystal Dust",    # Purple
    "Dream Sparkles",  # Pink
]

# Distinct pitch centres across colour families.
PITCH_OFFSETS = [-5, 0, 4, -2, 7, -7, 9, 12]


def midi_to_frequency(midi):
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def smooth(values, samples):
    samples = max(1, int(samples))

    if samples == 1:
        return values

    kernel = np.ones(samples) / samples
    left = samples // 2
    right = samples - 1 - left

    padded = np.pad(values, (left, right), mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def colour_envelopes(features, sample_count):
    distributions = np.asarray(
        features["region_distributions"],
        dtype=np.float64,
    )

    if distributions.shape != (8, 8):
        raise ValueError("Expected eight colour regions.")

    timeline = np.linspace(0, 1, sample_count)
    positions = np.linspace(0, 1, 8)

    envelopes = []

    for colour_index in range(8):
        values = np.interp(
            timeline,
            positions,
            distributions[:, colour_index],
        )

        envelopes.append(
            smooth(values, SAMPLE_RATE // 5)
        )

    return np.asarray(envelopes)


def make_material(index, frequency, t, rng):
    """
    Generate a different sonic texture for each hue family.
    All sounds are synthesized locally.
    """
    phase = 2 * np.pi * frequency * t

    if index == 0:
        # Red: dark, warm resonances.
        sound = (
            0.70 * np.sin(phase)
            + 0.24 * np.sin(phase * 1.005)
            + 0.12 * np.sin(phase * 2)
        )

    elif index == 1:
        # Orange: soft bell-like partials.
        sound = (
            0.58 * np.sin(phase)
            + 0.25 * np.sin(phase * 2.01)
            + 0.16 * np.sin(phase * 2.71)
        )
        sound *= 0.65 + 0.35 * np.sin(
            2 * np.pi * 0.43 * t
        ) ** 2

    elif index == 2:
        # Yellow: bright, gently shimmering chimes.
        sound = (
            0.42 * np.sin(phase)
            + 0.32 * np.sin(phase * 2.5)
            + 0.18 * np.sin(phase * 4.1)
        )
        sound *= 0.65 + 0.35 * np.sin(
            2 * np.pi * 1.4 * t
        ) ** 2

    elif index == 3:
        # Green: soft, organic movement.
        modulation = 1.0 + 0.012 * np.sin(
            2 * np.pi * 0.21 * t
        )
        sound = (
            0.72 * np.sin(phase * modulation)
            + 0.22 * np.sin(phase * 1.5)
        )

    elif index == 4:
        # Cyan: airy glass with a quiet filtered noise bed.
        noise = rng.standard_normal(len(t))
        airy = smooth(noise, 30)

        sound = (
            0.42 * np.sin(phase * 2.01)
            + 0.26 * np.sin(phase * 3.07)
            + 0.45 * airy
        )

    elif index == 5:
        # Blue: deep, slowly moving underwater resonance.
        movement = 0.72 + 0.28 * np.sin(
            2 * np.pi * 0.16 * t
        )
        sound = (
            0.75 * np.sin(phase * 0.5)
            + 0.22 * np.sin(phase * 1.01)
        ) * movement

    elif index == 6:
        # Purple: inharmonic crystalline texture.
        sound = (
            0.40 * np.sin(phase * 1.41)
            + 0.30 * np.sin(phase * 2.73)
            + 0.20 * np.sin(phase * 4.19)
        )

    else:
        # Pink: floating sparkling particles.
        sound = (
            0.34 * np.sin(phase * 2)
            + 0.26 * np.sin(phase * 3.5)
            + 0.20 * np.sin(phase * 5.1)
        )

        sparkle = np.maximum(
            0,
            np.sin(2 * np.pi * 2.8 * t)
        ) ** 8

        sound *= 0.2 + 0.8 * sparkle

    return sound


def map_image_to_notes(features):
    """
    Return region descriptions compatible with app.py.
    """
    brightness = float(features["brightness"])
    root_midi = 48 + 12 * brightness

    notes = []

    for region_index, distribution in enumerate(
        features["region_distributions"]
    ):
        weights = np.asarray(distribution, dtype=float)
        dominant_index = int(np.argmax(weights))

        frequency = midi_to_frequency(
            root_midi + PITCH_OFFSETS[dominant_index]
        )

        layers = []

        for index, weight in enumerate(weights):
            if weight >= 0.02:
                layers.append({
                    "hue_index": index,
                    "material": MATERIALS[index],
                    "frequency": round(
                        midi_to_frequency(
                            root_midi + PITCH_OFFSETS[index]
                        ),
                        2,
                    ),
                    "weight": float(weight),
                })

        notes.append({
            "region": region_index + 1,
            "frequency": round(frequency, 2),
            "color": features["region_colors"][region_index],
            "material": MATERIALS[dominant_index],
            "layers": layers,
            "diversity": features["region_diversities"][region_index],
        })

    return notes


def generate_sound(features, mood="Echo", intensity=0.5):
    if mood not in MOODS:
        raise ValueError("Invalid sound mode.")

    if not 0 <= intensity <= 1:
        raise ValueError("Intensity must be between 0 and 1.")

    rng = np.random.default_rng(42)

    brightness = float(features["brightness"])
    saturation = float(features["saturation"])
    diversity = float(features["color_diversity"])

    notes = map_image_to_notes(features)

    count = int(DURATION * SAMPLE_RATE)
    t = np.arange(count) / SAMPLE_RATE

    envelopes = colour_envelopes(features, count)

    root_midi = 48 + 12 * brightness
    audio = np.zeros(count, dtype=np.float64)

    for index in range(8):
        weights = envelopes[index]

        if np.max(weights) < 0.001:
            continue

        frequency = midi_to_frequency(
            root_midi + PITCH_OFFSETS[index]
        )

        material = make_material(
            index,
            frequency,
            t,
            rng,
        )

        # More represented colours become more audible.
        presence = np.sqrt(
            np.clip(weights, 0, 1)
        )

        # Saturation increases texture presence.
        gain = (
            0.10
            + 0.20 * intensity
            + 0.10 * saturation
        )

        audio += gain * presence * material

    # Atmospheric background, reduced for colourful images.
    drone_frequency = midi_to_frequency(root_midi - 12)
    drone = np.sin(
        2 * np.pi * drone_frequency * t
    )

    audio += (
        0.025 + 0.045 * (1 - diversity)
    ) * drone

    if mood == "Echo":
        original = audio.copy()

        for seconds, strength in [
            (0.38, 0.42),
            (0.91, 0.26),
        ]:
            delay = int(seconds * SAMPLE_RATE)
            audio[delay:] += original[:-delay] * strength

    elif mood == "Flow":
        motion = (
            0.75
            + 0.25 * np.sin(
                2 * np.pi * 0.13 * t
            )
        )
        audio *= motion

    elif mood == "Pulse":
        pulse = np.maximum(
            0,
            np.sin(2 * np.pi * 2.6 * t)
        ) ** 2

        audio *= 0.25 + 0.75 * pulse

    fade_in = np.minimum(1, t / 1.0)
    fade_out = np.minimum(1, (DURATION - t) / 1.5)

    audio *= np.maximum(
        0,
        np.minimum(fade_in, fade_out),
    )

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
