# app.py

import streamlit as st
from PIL import Image
import io

from image_processing import (
    remove_background,
    finalize_image
)

st.set_page_config(page_title="Background Removal Tool", layout="centered")
st.title("Background Removal & Resizing Tool")

# --- Sidebar Configuration ---
st.sidebar.header("Configuration")

# Background removal config
model_options = ["silueta", "u2net", "isnet-general-use"]
selected_models = st.sidebar.multiselect("Select Models", model_options, default=["isnet-general-use"])
original_bg_col = st.sidebar.color_picker("Original BG Color (for despill)", value="#ffffff")
original_bg_tuple = tuple(int(original_bg_col.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

threshold_white_areas = st.sidebar.slider("Threshold for White Areas", 0, 255, 245)
soft_despill_enabled = st.sidebar.checkbox("Soft Despill", value=True)
boost_alpha_factor = st.sidebar.slider("Boost Alpha Factor", 0.0, 3.0, 1.5, 0.1)
lighten_alpha_radius = st.sidebar.slider("Lighten Alpha (blur radius)", 0, 10, 1)

# NEW Feather edges
feather_edges_radius = st.sidebar.slider("Feather Edges Radius", 0, 20, 0)

# Finalizing config
padding_percentage = st.sidebar.slider("Padding Percentage", 0, 50, 15)
background_mode = st.sidebar.selectbox(
    "Background Mode",
    ["random", "fixed", "transparent", "pastel", "neon", "brand", "grey", "earth", "retro"]
)
fixed_bg_col = st.sidebar.color_picker("Fixed BG Color (if chosen)", value="#ffffff")
fixed_bg_tuple = tuple(int(fixed_bg_col.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

save_as_jpg = st.sidebar.checkbox("Save as JPG", value=False)

# Size config
width = st.sidebar.number_input("Output Width", value=1200, min_value=50, max_value=5000, step=50)
height = st.sidebar.number_input("Output Height", value=1200, min_value=50, max_value=5000, step=50)


# --- Main UI for file uploads ---
uploaded_files = st.file_uploader(
    "Upload your image(s) here (PNG/JPG/JPEG)",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    st.write("### Preview & Download Results")

    for uploaded_file in uploaded_files:
        # Read the uploaded file as a PIL image
        input_data = uploaded_file.read()
        input_image = Image.open(io.BytesIO(input_data)).convert("RGBA")

        # Process / remove background
        cutout_image = remove_background(
            input_image,
            models_to_use=selected_models,
            original_bg_color=original_bg_tuple,
            soft_despill_enabled=soft_despill_enabled,
            boost_alpha_factor=boost_alpha_factor,
            lighten_alpha_radius=lighten_alpha_radius,
            threshold_white_areas=threshold_white_areas,
            feather_edges_radius=feather_edges_radius  # <-- pass new param here
        )

        # Finalize
        final_img = finalize_image(
            cutout_image,
            padding_percentage=padding_percentage,
            background_mode=background_mode,
            fixed_background_color=fixed_bg_tuple,
            output_size=(width, height),
            save_as_jpg=save_as_jpg
        )

        # Display in Streamlit
        st.subheader(f"Preview: {uploaded_file.name}")
        st.image(final_img, use_column_width=True)

        # Provide download
        download_buf = io.BytesIO()
        if save_as_jpg:
            final_img.save(download_buf, format="JPEG", quality=95)
            dl_format = "image/jpeg"
            file_ext = "jpg"
        else:
            final_img.save(download_buf, format="PNG")
            dl_format = "image/png"
            file_ext = "png"

        st.download_button(
            label="Download Processed Image",
            data=download_buf.getvalue(),
            file_name=f"{uploaded_file.name}_processed.{file_ext}",
            mime=dl_format
        )
