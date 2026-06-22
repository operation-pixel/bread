import streamlit as st
st.session_state.bread_data.to_excel(EXCEL_FILE, index=False, engine="openpyxl")


st.title("About")
st.write("This app helps manage bread production and inventory.")
st.write("Use the sidebar to navigate to Bread Overview or Manage Bread.")


import os
import streamlit as st
final = "burger.jpeg"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(APP_DIR, "pages", "Images", final)

st.image(image_path, caption="Burger", width=100)


