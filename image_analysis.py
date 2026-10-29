
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_FILE_BYTES = 25 * 1024 * 1024

COLOR_NAMES = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Cyan",
    "Blue",
    "Purple",
    "Pink",
]


def get_color_distribution(hsv_array):
    """
    Measure the proportion of different hue families.

    Very pale or dark pixels are excluded from hue
    classification because their hue is less reliable.
    """
    hue = hsv_array[:, :, 0]
    saturation = hsv_array[:, :, 1]
    value = hsv_array[:, :, 2]

    valid = (saturation > 0.12) & (value > 0.12)

    if not np.any(valid):
        return [0.0] * 8

    selected_hues = hue[valid]

    # Rotate the hue wheel so that red is centred
    # around the first category.
    shifted = (selected_hues + 1 / 16) % 1.0

    bins = np.floor(shifted * 8).astype(int)
    bins = np.clip(bins, 0, 7)

    counts = np.bincount(bins, minlength=8)
    distribution = counts / counts.sum()

    return distribution.tolist()


def calculate_color_diversity(distribution):
    """
    Normalized entropy:
    0 = one dominant colour family
    1 = eight equally represented colour families
    """
    values = np.asarray(distribution, dtype=np.float64)
    nonzero = values[values > 0]

    if len(nonzero) == 0:
        return 0.0

    entropy = -np.sum(nonzero * np.log(nonzero))
    return float(entropy / np.log(8))


def analyze_image(file_bytes: bytes):
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_BYTES:
        raise ValueError("Image must be smaller than 25 MB.")

    try:
        with Image.open(BytesIO(file_bytes)) as source:
            source.verify()

        with Image.open(BytesIO(file_bytes)) as source:
            source = ImageOps.exif_transpose(source)
            source.thumbnail((800, 800))
            image = source.convert("RGB")

    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
    ) as exc:
        raise ValueError(
            "This image could not be read. "
            "Try another JPG, PNG, or WEBP file."
        ) from exc

    hsv = np.asarray(image.convert("HSV"), dtype=np.float32) / 255.0
    rgb = np.asarray(image, dtype=np.float32)

    brightness = float(np.mean(hsv[:, :, 2]))
    saturation = float(np.mean(hsv[:, :, 1]))

    angles = hsv[:, :, 0] * (2 * np.pi)
    weights = hsv[:, :, 1]

    x = float(np.sum(np.cos(angles) * weights))
    y = float(np.sum(np.sin(angles) * weights))

    if x * x + y * y > 1e-8:
        hue = float((np.arctan2(y, x) / (2 * np.pi)) % 1.0)
    else:
        hue = 0.0

    # Divide the image into eight vertical regions.
    rgb_regions = np.array_split(rgb, 8, axis=1)
    hsv_regions = np.array_split(hsv, 8, axis=1)

    region_colors = []
    region_distributions = []
    region_diversities = []

    for rgb_region, hsv_region in zip(rgb_regions, hsv_regions):
        mean_rgb = rgb_region.mean(axis=(0, 1))

        region_colors.append(
            tuple(int(round(v)) for v in mean_rgb)
        )

        distribution = get_color_distribution(hsv_region)
        region_distributions.append(distribution)

        region_diversities.append(
            calculate_color_diversity(distribution)
        )

    average_rgb = tuple(
        int(round(v)) for v in rgb.mean(axis=(0, 1))
    )

    overall_distribution = get_color_distribution(hsv)

    color_diversity = calculate_color_diversity(
        overall_distribution
    )

    return image, {
        "brightness": brightness,
        "saturation": saturation,
        "hue": hue,
        "average_rgb": average_rgb,
        "region_colors": region_colors,
        "color_distribution": overall_distribution,
        "color_diversity": color_diversity,
        "region_distributions": region_distributions,
        "region_diversities": region_diversities,
        "color_names": COLOR_NAMES,
    }
