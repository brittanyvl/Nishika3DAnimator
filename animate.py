import streamlit as st
from PIL import Image
import cv2
import numpy as np
import imageio
from moviepy.editor import ImageSequenceClip


st.set_page_config(layout="wide")

# Helper function to crop images to the same aspect ratio
def crop_to_minimum_size(images):
    # Find minimum width and height among all images
    min_width = min(image.size[0] for image in images)
    min_height = min(image.size[1] for image in images)

    cropped_images = []

    for img in images:
        # Convert to numpy array for processing
        img_array = np.array(img)
        height, width = img_array.shape[:2]

        # Calculate cropping coordinates
        start_x = (width - min_width) // 2
        start_y = (height - min_height) // 2

        # Crop the image
        cropped_img = img_array[start_y:start_y + min_height, start_x:start_x + min_width]
        cropped_images.append(cropped_img)

    return cropped_images


# Helper function to create an animated gif
def create_gif(images, output_path, duration=0.3):
    imageio.mimsave(output_path, images, duration=duration, loop=0)  # loop=0 for infinite looping


# Helper function to create an mp4 video
def create_mp4(images, output_path, fps=10, duration=10):
    clip = ImageSequenceClip([Image.fromarray(img) for img in images], fps=fps)
    # Set the duration of the video
    clip = clip.set_duration(duration)
    clip.write_videofile(output_path, codec="libx264")


# Streamlit app
st.title("Nishika N8000 3D Image Animator")

# Create a two-column layout
col1, col2 = st.columns(2)

with col1:
    st.write("Upload 4 images taken from the Nishika N8000 camera to create a 3D animated GIF or MP4 video.")
    uploaded_files = st.file_uploader("Upload the 4 images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    # Output format options
    output_format = st.selectbox("Choose output format", ("GIF", "MP4"))

    # Add a length input for MP4
    if output_format == "MP4":
        video_length = st.slider("Select video length (seconds)", 1, 30, 10)

with col2:
    if uploaded_files and len(uploaded_files) == 4:
        images = []

        # Load images
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            images.append(image)

        # Crop images to the same size based on minimum dimensions
        cropped_images = crop_to_minimum_size(images)

        # Process the output based on the selected format
        if output_format == "GIF":
            gif_path = "output.gif"
            create_gif([Image.fromarray(img) for img in cropped_images], gif_path)
            st.image(gif_path, caption="3D Animated GIF", use_column_width=True)

            # Provide a download button for the GIF
            with open(gif_path, "rb") as f:
                st.download_button("Download GIF", f, file_name="nishika_3d.gif", mime="image/gif")

        elif output_format == "MP4":
            mp4_path = "output.mp4"
            fps = len(cropped_images) / video_length  # Calculate frames per second based on selected length
            create_mp4(cropped_images, mp4_path, fps=fps, duration=video_length)

            # Provide a video player for the MP4
            st.video(mp4_path)

            # Provide a download button for the MP4
            with open(mp4_path, "rb") as f:
                st.download_button("Download MP4", f, file_name="nishika_3d.mp4", mime="video/mp4")
