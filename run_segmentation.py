"""
CLI script for batch cell segmentation.

Usage:
    uv run python run_segmentation.py
    uv run python run_segmentation.py --image data/raw/A172/2.5k/A8-1_181024_1315.png
    uv run python run_segmentation.py --image data/raw/A172/2.5k/ --batch
"""

import argparse
from pathlib import Path

from cell_segmentation import CellSegmentationModel, prepare_image, plot_results, load_image


def run_single(image_path: str, output_dir: str = "data/processed") -> None:
    """Segment a single image and save the result."""

    print(f"📂 Loading image: {image_path}")
    img = load_image(image_path)
    img_processed = prepare_image(image_path, resize=True, size=(512, 512))

    print("🔬 Running segmentation...")
    model = CellSegmentationModel()
    masks, cell_count = model.segment(img_processed)

    print(f"✅ Found {cell_count} cells!")

    # Save result
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_name = Path(image_path).stem
    save_path = output_dir / f"{image_name}_segmented.png"

    plot_results(img_processed, masks, cell_count, save_path=str(save_path))


def run_batch(folder_path: str, output_dir: str = "data/processed") -> None:
    """Segment all images in a folder and save results."""

    folder = Path(folder_path)
    images = list(folder.glob("*.png")) + list(folder.glob("*.tif"))

    if not images:
        print(f"❌ No images found in {folder_path}")
        return

    print(f"📂 Found {len(images)} images in {folder_path}")
    model = CellSegmentationModel()

    results = []

    for i, image_path in enumerate(images, 1):
        print(f"[{i}/{len(images)}] Processing {image_path.name}...")

        img_processed = prepare_image(str(image_path), resize=True, size=(512, 512))
        masks, cell_count = model.segment(img_processed)

        print(f"  ✅ Found {cell_count} cells!")
        results.append({"image": image_path.name, "cell_count": cell_count})

    # Print summary
    print("\n📊 Summary:")
    print(f"{'Image':<40} {'Cells':>6}")
    print("-" * 48)
    for r in results:
        print(f"{r['image']:<40} {r['cell_count']:>6}")
    print("-" * 48)
    total = sum(r["cell_count"] for r in results)
    print(f"{'Total cells':<40} {total:>6}")


def main():
    parser = argparse.ArgumentParser(description="Cell Segmentation CLI")
    parser.add_argument(
        "--image",
        type=str,
        default="sample/sample_cell_image.png",  
        help="Path to image or folder",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all images in folder",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed",
        help="Output directory for results",
    )

    args = parser.parse_args()

    if args.batch:
        run_batch(args.image, args.output)
    else:
        run_single(args.image, args.output)


if __name__ == "__main__":
    main()
