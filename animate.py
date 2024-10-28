import streamlit as st
from PIL import Image
import numpy as np
import imageio
from moviepy.editor import ImageSequenceClip
import re

# Set the page layout to wide
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


# Helper function to create an mp4 video with looping frames
def create_mp4(images, output_path, duration=10):
    fps = 10  # Set the same frame rate as the GIF
    total_frames = len(images)
    # Calculate how many times to loop the images to match the total duration
    frames_needed = fps * duration

    # Create a sequence of images to match the required total frames
    repeated_images = (images * ((frames_needed // total_frames) + 1))[:frames_needed]
    clip = ImageSequenceClip(repeated_images, fps=fps)  # Create the clip
    clip.write_videofile(output_path, codec="libx264")


# Function to sort files based on numeric values at the end of the filename
def sort_files_by_number(uploaded_files):
    def extract_number(filename):
        # Find a number at the end of the filename using regex
        match = re.search(r'(\d+)$', filename)
        return int(match.group(1)) if match else float('inf')  # Return inf if no number found

    # Sort the files based on extracted numbers
    return sorted(uploaded_files, key=lambda x: extract_number(x.name))


# Streamlit app
st.title("Wiggle to Reels for Nishika N8000 3D")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    1. **Scan** your film and crop out each half frame.  
    2. **Save** your images; if you include a number at the end, we will animate them in the specified order.  
    3. **Upload** your images and select either GIF or MP4. The MP4 file can be uploaded to Instagram as a reel.  
    4. If you selected MP4, you will be prompted to enter a video length; use the slider to select.  
    5. **Click submit** when you're ready to generate your video.  
    6. If you're happy, **click download** to save the animation to your computer.
    """)
with col2:
    uploaded_files = st.file_uploader("Upload the 4 images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    # Output format options
    output_format = st.selectbox("Choose output format", ("GIF", "MP4"))

    # Add a length input for MP4
    if output_format == "MP4":
        video_length = st.slider("Select video length (seconds)", 1, 30, 10)

    # Submit button to generate GIF/MP4
    submit_button = st.button("Submit")

with col3:
    if submit_button and uploaded_files and len(uploaded_files) == 4:
        # Sort the uploaded files by number in their names
        sorted_files = sort_files_by_number(uploaded_files)
        images = []

        # Load images
        for uploaded_file in sorted_files:
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
                st.download_button("Download GIF", f, file_name="wigglegram.gif", mime="image/gif")

        elif output_format == "MP4":
            mp4_path = "output.mp4"
            create_mp4(cropped_images, mp4_path, duration=video_length)  # Duration set by user

            # Provide a video player for the MP4
            st.video(mp4_path)

            # Provide a download button for the MP4
            with open(mp4_path, "rb") as f:
                st.download_button("Download MP4", f, file_name="wigglegram.mp4", mime="video/mp4")
