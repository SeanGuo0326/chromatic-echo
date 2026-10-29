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

MATERIALS = [
    "Warm Resonance", "Soft Bells", "Golden Chimes", "Organic Waves",
    "Air and Glass", "Deep Water", "Crystal Dust", "Dream Sparkles",
]
PITCH_OFFSETS = [-5, 0, 4, -2, 7, -7, 9, 12]


def midi_to_frequency(midi):
    return 440.0 * 2.0 ** ((midi - 69.0) / 12.0)


def smooth(values, samples):
    """Efficient moving average, preserving the input length."""
    values = np.asarray(values, dtype=np.float64)
    samples = max(1, int(samples))
    if samples == 1:
        return values.copy()
    left = samples // 2
    right = samples - 1 - left
    padded = np.pad(values, (left, right), mode="edge")
    cumulative = np.concatenate(([0.0], np.cumsum(padded)))
    return (cumulative[samples:] - cumulative[:-samples]) / samples


def colour_envelopes(features, sample_count):
    distributions = np.asarray(features["region_distributions"], dtype=float)
    if distributions.shape != (8, 8):
        raise ValueError("Expected eight regions with eight colour proportions each.")
    positions = np.linspace(0.0, 1.0, 8)
    timeline = np.linspace(0.0, 1.0, sample_count)
    return np.asarray([
        smooth(np.interp(timeline, positions, distributions[:, i]), SAMPLE_RATE // 6)
        for i in range(8)
    ])


def make_material(index, frequency, t, rng):
    """Eight distinct synthesized timbres, with no external audio files."""
    phase = 2 * np.pi * frequency * t
    if index == 0:
        return 0.7 * np.sin(phase) + 0.25 * np.sin(phase * 1.006) + 0.12 * np.sin(2 * phase)
    if index == 1:
        return 0.65 * np.sin(phase) + 0.23 * np.sin(phase * 2.01) + 0.16 * np.sin(phase * 2.71)
    if index == 2:
        return 0.48 * np.sin(phase) + 0.28 * np.sin(phase * 2.5) + 0.20 * np.sin(phase * 4.1)
    if index == 3:
        return 0.75 * np.sin(phase + 1.4 * np.sin(2 * np.pi * 0.24 * t)) + 0.2 * np.sin(phase * 1.5)
    if index == 4:
        noise = smooth(rng.standard_normal(len(t)), 20)
        return 0.52 * np.sin(phase * 2.01) + 0.27 * np.sin(phase * 3.07) + 0.7 * noise
    if index == 5:
        return 0.8 * np.sin(phase * 0.5) + 0.22 * np.sin(phase * 1.01)
    if index == 6:
        return 0.46 * np.sin(phase * 1.41) + 0.32 * np.sin(phase * 2.73) + 0.2 * np.sin(phase * 4.19)
    sparkle = np.maximum(0, np.sin(2 * np.pi * 3.0 * t)) ** 6
    return (0.42 * np.sin(phase * 2) + 0.28 * np.sin(phase * 3.5)) * (0.25 + 0.75 * sparkle)


def map_image_to_notes(features):
    """Keep the mapping format compatible with the existing app.py."""
    root_midi = 48 + 12 * float(features["brightness"])
    notes = []
    for region_index, distribution in enumerate(features["region_distributions"]):
        weights = np.asarray(distribution, dtype=float)
        dominant_index = int(np.argmax(weights))
        frequency = midi_to_frequency(root_midi + PITCH_OFFSETS[dominant_index])
        layers = []
        for index, weight in enumerate(weights):
            if weight >= 0.02:
                layers.append({
                    "hue_index": index,
                    "material": MATERIALS[index],
                    "frequency": round(midi_to_frequency(root_midi + PITCH_OFFSETS[index]), 2),
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


def add_event(audio, start, duration, frequency, material_index, amplitude, rng):
    """Place a short, smoothly enveloped sound event on the timeline."""
    start_sample = int(start * SAMPLE_RATE)
    if start_sample >= len(audio):
        return
    length = min(int(duration * SAMPLE_RATE), len(audio) - start_sample)
    if length <= 0:
        return
    t = np.arange(length) / SAMPLE_RATE
    signal = make_material(material_index, frequency, t, rng)
    attack = np.clip(t / 0.10, 0, 1)
    release = np.clip((duration - t) / max(0.25, duration * 0.55), 0, 1)
    envelope = np.minimum(attack, release) ** 1.2
    audio[start_sample:start_sample + length] += amplitude * signal * envelope


def generate_sound(features, mood="Echo", intensity=0.5):
    if mood not in MOODS:
        raise ValueError("Invalid sound mode.")
    if not 0 <= intensity <= 1:
        raise ValueError("Intensity must be between 0 and 1.")

    distributions = np.asarray(features["region_distributions"], dtype=float)
    if distributions.shape != (8, 8):
        raise ValueError("Expected eight regions with eight colour proportions each.")

    rng = np.random.default_rng(42)
    notes = map_image_to_notes(features)
    count = int(DURATION * SAMPLE_RATE)
    t = np.arange(count) / SAMPLE_RATE
    audio = np.zeros(count, dtype=np.float64)
    root_midi = 48 + 12 * float(features["brightness"])
    saturation = float(features["saturation"])
    diversity = float(features["color_diversity"])

    # A quiet atmospheric bed connects the eight regions.
    envelopes = colour_envelopes(features, count)
    for index in range(8):
        if np.max(envelopes[index]) < 0.001:
            continue
        frequency = midi_to_frequency(root_midi + PITCH_OFFSETS[index])
        texture = make_material(index, frequency, t, rng)
        audio += (0.025 + 0.035 * intensity) * np.sqrt(np.clip(envelopes[index], 0, 1)) * texture

    # Each region becomes a distinct event in time. Reordering the
    # regions now changes the audible progression, not only the drone.
    region_seconds = DURATION / 8
    for region_index, weights in enumerate(distributions):
        ranked = np.argsort(weights)[::-1]
        start = region_index * region_seconds
        for rank, colour_index in enumerate(ranked[:3]):
            weight = float(weights[colour_index])
            if weight < 0.025:
                continue
            colour_index = int(colour_index)
            # Primary material starts at the region boundary; supporting
            # materials enter later, making transitions easier to hear.
            onset = start + (0.0 if rank == 0 else 0.35 * rank)
            duration = (2.65 if mood == "Flow" else 1.85) + 0.35 * weight
            frequency = midi_to_frequency(root_midi + PITCH_OFFSETS[colour_index])
            # Small melodic lift within each region, derived from region index.
            if rank == 1:
                frequency *= 2 ** (3 / 12)
            elif rank == 2:
                frequency *= 2 ** (7 / 12)
            amplitude = (0.12 + 0.20 * intensity) * np.sqrt(weight)
            add_event(audio, onset, duration, frequency, colour_index, amplitude, rng)

        if mood == "Pulse":
            dominant = int(ranked[0])
            frequency = midi_to_frequency(root_midi + PITCH_OFFSETS[dominant] + 12)
            for beat in range(3):
                add_event(audio, start + 0.20 + beat * 0.56, 0.42, frequency,
                          dominant, (0.06 + 0.10 * intensity) * np.sqrt(max(0, weights[dominant])), rng)

    # Soft low-frequency grounding; deliberately quieter than events.
    drone_frequency = midi_to_frequency(root_midi - 12)
    audio += (0.008 + 0.018 * (1 - diversity)) * np.sin(2 * np.pi * drone_frequency * t)

    if mood == "Echo":
        dry = audio.copy()
        for seconds, strength in ((0.42, 0.30), (0.96, 0.16)):
            delay = int(seconds * SAMPLE_RATE)
            audio[delay:] += dry[:-delay] * strength
    elif mood == "Flow":
        audio *= 0.82 + 0.18 * np.sin(2 * np.pi * 0.12 * t)

    fade_in = np.minimum(1.0, t / 0.35)
    fade_out = np.minimum(1.0, (DURATION - t) / 0.9)
    audio *= np.maximum(0, np.minimum(fade_in, fade_out))
    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio *= 0.82 / peak

    pcm = (audio * 32767).astype("<i2")
    buffer = BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        wav.writeframes(pcm.tobytes())
    return buffer.getvalue(), notes
