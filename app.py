"""
Streamlit app for interactive cell segmentation.
"""

import streamlit as st
import numpy as np
import tempfile
import os
from PIL import Image

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
st.write("Upload a microscopy image to detect and count cells automatically.")

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

model = load_model(diameter, flow_threshold, cellprob_threshold)

# ── File upload ────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader("Upload image", type=["png", "tif", "jpg"])

if uploaded_file:
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
        f.write(uploaded_file.read())
        tmp_path = f.name

    # Load original for display
    img_original = load_image(tmp_path)

    # Preprocessed image for segmentation
    img_processed = prepare_image(tmp_path, resize=True, size=(512, 512))

    # Run segmentation
    with st.spinner("🔬 Detecting cells... (1-2 min on CPU)"):
        masks, cell_count = model.segment(img_processed)

    # ── Results ────────────────────────────────────────────────────────────────
    st.success(f"✅ Detected **{cell_count} cells**!")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Original Image")
        st.image(img_original, width='stretch', clamp=True)

    with col2:
        st.subheader("Segmentation Mask")
        st.image(masks_to_color(masks), width='stretch')

    with col3:
        st.subheader("Overlay")
        st.image(
            overlay_masks(img_processed, masks, alpha=overlay_alpha),
            width='stretch'
        )

    os.unlink(tmp_path)
