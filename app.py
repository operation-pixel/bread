import streamlit as st
import os

st.title("About")
st.write("This app helps manage bread production and inventory.")
st.write("Use the sidebar to navigate to Bread Overview or Manage Bread.")


image_dir = os.path.join("static", "images")
st.write("Image directory:", image_dir)


# List all files in the folder
if os.path.exists(image_dir):
    files = os.listdir(image_dir)
    st.write("Files found in static/image:", files)
    st.write("Please help")

# Show the hotdog image
hotdog_path = os.path.join(image_dir, "eggy_bread.jpeg")  # adjust extension if it's .png
if os.path.exists(hotdog_path):
    st.image(hotdog_path, caption="Hotdog", width=300)
else:
    st.error(f"Hotdog image not found at {hotdog_path}")
