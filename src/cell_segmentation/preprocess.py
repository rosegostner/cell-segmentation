"""
Image preprocessing utilities for cell segmentation.
"""

import numpy as np
from PIL import Image
from cellpose import io


def load_image(path: str) -> np.ndarray:
    """
    Load an image from disk.

    Args:
        path: Path to image file (png, tif, jpg).

    Returns:
        Image as numpy array.
    """
    return io.imread(path)


def resize_image(img: np.ndarray, size: tuple[int, int] = (512, 512)) -> np.ndarray:
    """
    Resize image to given size.

    Args:
        img:  Input image as numpy array.
        size: Target size as (width, height). Default: (512, 512).

    Returns:
        Resized image as numpy array.
    """
    pil_img = Image.fromarray(img)
    pil_img = pil_img.resize(size)
    return np.array(pil_img)


def normalize_image(img: np.ndarray) -> np.ndarray:
    """
    Normalize image to range [0, 1].

    Args:
        img: Input image as numpy array (uint8 or float).

    Returns:
        Normalized image as float32 array.
    """
    img = img.astype(np.float32)
    img_min, img_max = img.min(), img.max()

    if img_max - img_min == 0:
        return img

    return (img - img_min) / (img_max - img_min)


def prepare_image(
    path: str,
    resize: bool = True,
    size: tuple[int, int] = (512, 512),
) -> np.ndarray:
    """
    Full preprocessing pipeline: load → resize → normalize.

    Args:
        path:   Path to image file.
        resize: Whether to resize the image. Default: True.
        size:   Target size if resizing. Default: (512, 512).

    Returns:
        Preprocessed image ready for segmentation.
    """
    img = load_image(path)

    if resize:
        img = resize_image(img, size)

    img = normalize_image(img)

    return img
