import streamlit as st
import numpy as np
from PIL import Image

st.set_page_config(page_title="Face Attendance System", layout="centered")

st.title("🧠 Face Attendance System (Web Demo)")
st.caption("Browser-based demo | Local system uses OpenCV")

img = st.camera_input("📸 Capture your face")

if img:
    image = Image.open(img)
    st.image(image, caption="Captured Image", use_column_width=True)

    # Dummy confidence for demo
    st.success("Face detected successfully!")
    st.info("This is a web demo. Full real-time system runs locally.")
