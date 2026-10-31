"""
Streamlit app for interactive cell segmentation.
"""

from pathlib import Path
import os
import tempfile

import streamlit as st

from cell_segmentation import (
    CellSegmentationModel,
    prepare_image,
    load_image,
    overlay_masks,
    masks_to_color,
)


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cell Segmentation",
    page_icon="🔬",
    layout="wide",
)

# ── Title ──────────────────────────────────────────────────────────────────────
st.title("🔬 Cell Segmentation App")
st.write("Try the demo image or upload your own microscopy image to detect cells.")

# ── Sidebar settings ───────────────────────────────────────────────────────────
st.sidebar.header("⚙️ Settings")

diameter = st.sidebar.slider(
    "Cell diameter (px)", min_value=10, max_value=100, value=30, step=5
)
flow_threshold = st.sidebar.slider(
    "Flow threshold", min_value=0.0, max_value=1.0, value=0.4, step=0.05
)
cellprob_threshold = st.sidebar.slider(
    "Cell probability threshold", min_value=-5.0, max_value=5.0, value=0.0, step=0.5
)
overlay_alpha = st.sidebar.slider(
    "Overlay transparency", min_value=0.1, max_value=0.9, value=0.5, step=0.1
)


# ── Model (cached) ─────────────────────────────────────────────────────────────
@st.cache_resource
def load_model(diameter, flow_threshold, cellprob_threshold):
    return CellSegmentationModel(
        diameter=diameter,
        flow_threshold=flow_threshold,
        cellprob_threshold=cellprob_threshold,
    )


# ── Choose image ───────────────────────────────────────────────────────────────
source = st.radio("Image source", ["Demo image", "Upload your own image"])

image_path = None
tmp_path = None

if source == "Demo image":
    demo_path = Path(__file__).resolve().parent / "sample" / "sample_cell_image.png"
    st.caption("Demo image from LIVECell · CC BY-NC 4.0")

    if st.button("Run demo segmentation"):
        if demo_path.is_file():
            image_path = demo_path
        else:
            st.error("Demo image not found in sample/sample_cell_image.png")

else:
    uploaded_file = st.file_uploader(
        "Upload image", type=["png", "tif", "tiff", "jpg", "jpeg"]
    )

    if uploaded_file is not None:
        # Keep the original extension so the image loader can recognize the format.
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(uploaded_file.getvalue())
            tmp_path = f.name
        image_path = Path(tmp_path)


# ── Segment and display results ────────────────────────────────────────────────
if image_path is not None:
    try:
        img_original = load_image(str(image_path))
        img_processed = prepare_image(
            str(image_path), resize=True, size=(512, 512)
        )

        with st.spinner("🔬 Detecting cells... (1–2 min on CPU)"):
            model = load_model(diameter, flow_threshold, cellprob_threshold)
            masks, cell_count = model.segment(img_processed)

        st.success(f"✅ Detected **{cell_count} cells**!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("Original Image")
            st.image(img_original, width="stretch", clamp=True)

        with col2:
            st.subheader("Segmentation Mask")
            st.image(masks_to_color(masks), width="stretch")

        with col3:
            st.subheader("Overlay")
            st.image(
                overlay_masks(img_processed, masks, alpha=overlay_alpha),
                width="stretch",
            )
    finally:
        # Only uploaded images create a temporary file. Never delete the demo image.
        if tmp_path is not None:
            os.unlink(tmp_path)