import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

st.set_page_config(page_title="Image Transformation App", layout="wide")
st.title("🖼️ Image Transformation Tool")
st.markdown("Upload or capture an image, apply transformations, and download the result.")

# --------------------------
# Session State Initialization
# --------------------------
if "original_image" not in st.session_state:
    st.session_state.original_image = None
if "transformed_image" not in st.session_state:
    st.session_state.transformed_image = None

# --------------------------
# Controls in two columns (top part)
# --------------------------
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 📸 Image Source")
    source = st.radio(
        "Choose image source:",
        ["Upload Image", "Use Camera"],
        index=0,
        help="Upload a file or take a picture with your camera."
    )

    image = None
    if source == "Upload Image":
        uploaded_file = st.file_uploader(
            "Drag and drop or browse files:",
            type=["jpg", "jpeg", "png"],
            help="Max 200MB"
        )
        if uploaded_file:
            pil_img = Image.open(uploaded_file).convert("RGB")
            image = np.array(pil_img)
    else:
        camera_image = st.camera_input("📷 Take a picture")
        if camera_image:
            pil_img = Image.open(camera_image).convert("RGB")
            image = np.array(pil_img)

    if image is not None:
        if st.session_state.original_image is None or not np.array_equal(image, st.session_state.original_image):
            st.session_state.original_image = image.copy()
            st.session_state.transformed_image = None

    if st.session_state.original_image is not None:
        st.markdown("**Current image loaded ✅**")

with col2:
    st.markdown("### 🛠️ Transformations")
    transform_type = st.selectbox(
        "What would you like to do?",
        [
            "None",
            "Rotate 🔄",
            "Scale 🔍",
            "Crop ✂️",
            "Affine Transform 🎯",
            "Perspective Transform 🧊",
            "Brightness Adjustment 💡",
            "Contrast Adjustment ⚡",
            "Flip 🔄",
            "Grayscale Conversion "
        ],
        help="Pick a transformation."
    )

# --------------------------
# Show Original Image below controls
# --------------------------
if st.session_state.original_image is not None:
    st.subheader("📌 Original Image")
    st.image(st.session_state.original_image, use_container_width=True)
else:
    st.info("Please upload or capture an image to begin.")
    st.stop()

# --------------------------
# Base image for transform
# --------------------------
base_image = st.session_state.original_image.copy()
transformed_image = base_image.copy()

# --------------------------
# Transformations options in expandable sections (for neatness)
# --------------------------
if transform_type == "Rotate 🔄":
    angle = st.slider("Rotation Angle", -180, 180, 0)
    h, w = transformed_image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    transformed_image = cv2.warpAffine(transformed_image, matrix, (w, h))
    st.subheader(f"🌀 Rotated {angle}°")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Scale 🔍":
    scale = st.slider("Scale Factor", 0.1, 3.0, 1.0)
    transformed_image = cv2.resize(transformed_image, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
    st.subheader(f"🔍 Scaled {scale}x")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Crop ✂️":
    h, w = transformed_image.shape[:2]
    if w < 2 or h < 2:
        st.error("Image too small to crop.")
    else:
        with st.expander("Crop Options"):
            x1 = st.slider("X Start", 0, w - 2, 0)
            x2 = st.slider("X End", x1 + 1, w, w)
            y1 = st.slider("Y Start", 0, h - 2, 0)
            y2 = st.slider("Y End", y1 + 1, h, h)

        transformed_image = transformed_image[y1:y2, x1:x2]
        st.subheader("✂️ Cropped Image")
        st.image(transformed_image, use_container_width=True)

elif transform_type == "Affine Transform 🎯":
    h, w = transformed_image.shape[:2]
    st.markdown("Using sample affine transformation.")
    pts1 = np.float32([[50, 50], [200, 50], [50, 200]])
    pts2 = np.float32([[10, 100], [200, 50], [100, 250]])
    matrix = cv2.getAffineTransform(pts1, pts2)
    transformed_image = cv2.warpAffine(transformed_image, matrix, (w, h))
    st.subheader("🎯 Affine Transform Applied")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Perspective Transform 🧊":
    h, w = transformed_image.shape[:2]
    st.markdown("Using sample perspective transformation.")
    pts1 = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
    pts2 = np.float32([[0, 0], [w - 100, 50], [50, h - 100], [w - 50, h - 50]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    transformed_image = cv2.warpPerspective(transformed_image, matrix, (w, h))
    st.subheader("🧊 Perspective Transform Applied")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Brightness Adjustment 💡":
    brightness = st.slider("Brightness", -100, 100, 0)
    temp_img = transformed_image.astype(np.int16) + brightness
    temp_img = np.clip(temp_img, 0, 255).astype(np.uint8)
    transformed_image = temp_img
    st.subheader(f"💡 Brightness adjusted by {brightness}")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Contrast Adjustment ⚡":
    contrast = st.slider("Contrast", 0.1, 3.0, 1.0)
    temp_img = transformed_image.astype(np.float32) * contrast
    temp_img = np.clip(temp_img, 0, 255).astype(np.uint8)
    transformed_image = temp_img
    st.subheader(f"⚡ Contrast adjusted by {contrast}")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Flip 🔄":
    flip_mode = st.selectbox(
        "Flip Mode:",
        ["➡️ Horizontal", "⬇️ Vertical"],
        help="Flip image horizontally or vertically."
    )
    if flip_mode == "➡️ Horizontal":
        transformed_image = cv2.flip(transformed_image, 1)
    elif flip_mode == "⬇️ Vertical":
        transformed_image = cv2.flip(transformed_image, 0)
    st.subheader(f"🔄 Flipped {flip_mode}")
    st.image(transformed_image, use_container_width=True)

elif transform_type == "Grayscale Conversion ":
    gray_img = cv2.cvtColor(transformed_image, cv2.COLOR_RGB2GRAY)
    transformed_image = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2RGB)
    st.subheader(" Grayscale Image")
    st.image(transformed_image, use_container_width=True)

# --------------------------
# Download Button for transformed image
# --------------------------
if transform_type != "None":
    pil_result = Image.fromarray(transformed_image)
    buffer = io.BytesIO()
    pil_result.save(buffer, format="PNG")
    byte_img = buffer.getvalue()

    st.download_button(
        label="📥 Download Transformed Image",
        data=byte_img,
        file_name="transformed_image.png",
        mime="image/png"
    )
