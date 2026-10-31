"""
Visualization utilities for cell segmentation results.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def masks_to_color(masks: np.ndarray) -> np.ndarray:
    """
    Convert integer mask to RGB color image.
    Each cell gets a unique color.

    Args:
        masks: 2D array where each cell has a unique integer ID.

    Returns:
        RGB image as uint8 array.
    """
    if masks.max() == 0:
        return np.zeros((*masks.shape, 3), dtype=np.uint8)

    # Normalize mask to [0, 1] and apply colormap
    normalized = masks.astype(float) / masks.max()
    colored = plt.cm.jet(normalized)[:, :, :3]  # drop alpha channel
    return (colored * 255).astype(np.uint8)


def overlay_masks(img: np.ndarray, masks: np.ndarray, alpha: float = 0.5) -> np.ndarray:
    """
    Overlay segmentation mask on original image.

    Args:
        img:   Original grayscale or RGB image.
        masks: 2D segmentation mask.
        alpha: Transparency of overlay (0=invisible, 1=opaque). Default: 0.5.

    Returns:
        Blended RGB image as uint8 array.
    """
    # Convert grayscale to RGB if needed
    if img.ndim == 2:
        img_rgb = np.stack([img, img, img], axis=-1)
    else:
        img_rgb = img.copy()

    # Normalize to uint8 if float
    if img_rgb.dtype != np.uint8:
        img_rgb = (img_rgb * 255).astype(np.uint8)

    colored_masks = masks_to_color(masks)

    # Blend original image with mask
    blended = (
        (1 - alpha) * img_rgb.astype(float) +
        alpha * colored_masks.astype(float)
    ).astype(np.uint8)

    return blended


def plot_results(
    img: np.ndarray,
    masks: np.ndarray,
    cell_count: int,
    save_path: str = None,
) -> None:
    """
    Plot original image, mask, and overlay side by side.

    Args:
        img:        Original image.
        masks:      Segmentation mask.
        cell_count: Number of detected cells.
        save_path:  Optional path to save the figure.
    """
    overlay = overlay_masks(img, masks)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    axes[0].imshow(img, cmap="gray")
    axes[0].set_title("Original Image")
    axes[0].axis("off")

    axes[1].imshow(masks_to_color(masks))
    axes[1].set_title(f"Segmentation Mask\n{cell_count} cells detected")
    axes[1].axis("off")

    axes[2].imshow(overlay)
    axes[2].set_title("Overlay")
    axes[2].axis("off")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"✅ Saved to {save_path}")

    plt.show()
