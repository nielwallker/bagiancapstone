import base64
import streamlit as st
from PIL import ImageOps, Image
import numpy as np
import tensorflow as tf

def set_background(image_file):
    """
    This function sets the background of a Streamlit app to an image specified by the given image file.

    Parameters:
        image_file (str): The path to the image file to be used as the background.

    Returns:
        None
    """
    with open(image_file, "rb") as f:
        img_data = f.read()
    b64_encoded = base64.b64encode(img_data).decode()
    style = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{b64_encoded});
            background-size: cover;
        }}
        </style>
    """
    st.markdown(style, unsafe_allow_html=True)

def classify(image, model, class_names, top_n=1):
    """
    This function takes an image, a model, and a list of class names and returns the top N predicted classes 
    and their confidence scores.

    Parameters:
        image (PIL.Image.Image): An image to be classified.
        model (tensorflow.keras.Model): A trained machine learning model for image classification.
        class_names (list): A list of class names corresponding to the classes that the model can predict.
        top_n (int): The number of top predictions to return.

    Returns:
        A list of tuples of the predicted class names and their confidence scores.
    """
    # Check if the image is grayscale
    if image.mode == 'L':
        # Convert grayscale image to 3-channel grayscale image
        image = image.convert('RGB')
    else:
        # Ensure the image is in RGB mode
        image = image.convert('RGB')

    # Resize the image to match the input shape expected by the model
    target_size = (200, 200)  # Ensure this matches your model's expected input size
    image = image.resize(target_size)

    # Convert image to numpy array and normalize
    image_array = np.array(image) / 255.0

    # Expand dimensions to match the input shape expected by the model
    image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension

    # Make prediction
    prediction = model.predict(image_array)

    # Get the top N predicted classes and their confidence scores
    top_indices = np.argsort(prediction[0])[-top_n:][::-1]
    top_classes = [(class_names[i], prediction[0][i]) for i in top_indices]

    return top_classes

# Example usage (commented out since we don't have the actual model and class names here):
# image = Image.open('path_to_your_image.jpg')
# model = tf.keras.models.load_model('path_to_your_model.h5')
# class_names = ['class1', 'class2', 'class3']  # replace with actual class names
# top_classes = classify(image, model, class_names, top_n=1)
# print(top_classes)
