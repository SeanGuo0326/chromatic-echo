
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_FILE_BYTES = 25 * 1024 * 1024


def analyze_image(file_bytes: bytes):
    """Analyze an image and return visual features."""
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

    brightness = float(np.mean(hsv[:, :, 2]))
    saturation = float(np.mean(hsv[:, :, 1]))

    # Calculate the circular mean of hue values.
    angles = hsv[:, :, 0] * (2 * np.pi)
    weights = hsv[:, :, 1]

    x = float(np.sum(np.cos(angles) * weights))
    y = float(np.sum(np.sin(angles) * weights))

    if x * x + y * y > 1e-8:
        hue = float((np.arctan2(y, x) / (2 * np.pi)) % 1.0)
    else:
        hue = 0.0

    # Divide the image into eight vertical regions.
    if image.width < 8:
        image = image.resize((8, max(1, image.height)))

    arr = np.asarray(image, dtype=np.float32)
    slices = np.array_split(arr, 8, axis=1)

    region_colors = [
        tuple(int(round(v)) for v in region.mean(axis=(0, 1)))
        for region in slices
    ]

    average_rgb = tuple(
        int(round(v)) for v in arr.mean(axis=(0, 1))
    )

    return image, {
        "brightness": brightness,
        "saturation": saturation,
        "hue": hue,
        "average_rgb": average_rgb,
        "region_colors": region_colors,
    }
  