import streamlit as st
from keras.models import load_model
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from util import classify, set_background
from datetime import datetime
import os
import auth_functions

# Set background
set_background('./bgrd/bg.jpg')

# Define CSS for the title, header, image name, and text boxes
st.markdown(
    """
    <style>
    .title-box, .header-box, .filename-box, .box, .button-box {
        border: 1px solid #000;
        padding: 10px;
        border-radius: 5px;
        background-color: #333;
        color: white;
        margin-top: 20px;
        text-align: center;
    }
    .title-box {
        font-size: 32px;
        font-weight: bold;
    }
    .header-box {
        font-size: 24px;
        font-weight: bold;
    }
    .filename-box {
        font-size: 18px;
    }
    .box h2, .box h3 {
        margin: 0;
    }
    .stButton>button {
        background-color: #333;
        color: white;
        border-radius: 5px;
        border: 1px solid #000;
    }
    .center-button {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True
)

# -------------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------------
# Function to check if user is logged in
def is_user_logged_in():
    return 'user_info' in st.session_state

# Authentication required for page access
if not is_user_logged_in():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # Add welcome message with a box
        st.markdown(
            """
            <div style='border: 2px solid #ddd; padding: 20px; border-radius: 10px; background-color: #000; color: #fff; text-align: center; margin-bottom: 20px;'>
                <h2>Welcome to Quality Cast App</h2>
            </div>
            """, unsafe_allow_html=True
        )

    # Authentication form layout
    do_you_have_an_account = col2.selectbox(
        label='Do you have an account?', 
        options=('Yes', 'No', 'I forgot my password'), 
        help='Select one option', 
        key='auth_select'
    )
    st.markdown('<style>select#auth_select { font-size: 18px; }</style>', unsafe_allow_html=True)
    auth_form = col2.form(key='Authentication form', clear_on_submit=False)
    email = auth_form.text_input(label='Email')
    password = auth_form.text_input(label='Password', type='password') if do_you_have_an_account in {'Yes', 'No'} else auth_form.empty()
    auth_notification = col2.empty()

    # Sign In
    if do_you_have_an_account == 'Yes' and auth_form.form_submit_button(label='Sign In', use_container_width=True, type='primary'):
        with auth_notification, st.spinner('Signing in'):
            auth_functions.sign_in(email, password)

    # Create Account
    elif do_you_have_an_account == 'No' and auth_form.form_submit_button(label='Create Account', use_container_width=True, type='primary'):
        with auth_notification, st.spinner('Creating account'):
            auth_functions.create_account(email, password)

    # Password Reset
    elif do_you_have_an_account == 'I forgot my password' and auth_form.form_submit_button(label='Send Password Reset Email', use_container_width=True, type='primary'):
        with auth_notification, st.spinner('Sending password reset link'):
            auth_functions.reset_password(email)

    # Authentication success and warning messages
    if 'auth_success' in st.session_state:
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success
    elif 'auth_warning' in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning
    else:
    # Your page content here for logged-in users
        st.write("You are Not logged in.")
else:
    # Set title
    st.markdown('<div class="title-box">Quality Cast</div>', unsafe_allow_html=True)

    # Set header
    st.markdown('<div class="header-box">Please upload a Casting Product Image</div>', unsafe_allow_html=True)

    # Upload file
    file = st.file_uploader('', type=['jpeg', 'jpg', 'png'])

    @st.cache
    # Load classifier
    model = load_model('./modelnew.h5')

    # Load class names
    with open('./model/labels.txt', 'r') as f:
        class_names = [line.strip().split(' ')[1] for line in f.readlines()]

    # Display image and classification results
    if file is not None:
        # Show the start button after file is uploaded
        if st.button('Start Prediction'):
            st.session_state.prediction_started = True

        # Display image and classification results if the start button is pressed
        if 'prediction_started' in st.session_state and st.session_state.prediction_started:
            # Create two columns for layout
            col1, col2 = st.columns(2)

            # Column 1: Image and file name
            with col1:
                image = Image.open(file).convert('RGB')
                st.image(image, use_column_width=True)
                st.markdown(f'<div class="filename-box">Uploaded file: {file.name}</div>', unsafe_allow_html=True)

            # Column 2: Classification result and donut chart
            with col2:
                # Check if prediction is already made
                if 'prediction_made' not in st.session_state:
                    # Classify image
                    top_classes = classify(image, model, class_names, top_n=1)

                    # Display the top class and its confidence score
                    top_class_name, top_conf_score = top_classes[0]
                    top_conf_percentage = top_conf_score * 100

                    # Get the index of the second class (other than the top class)
                    second_class_index = 1 if top_class_name == class_names[0] else 0

                    # Get the name and score of the second class
                    second_class_name = class_names[second_class_index]
                    second_conf_score = 1 - top_conf_score
                    second_conf_percentage = 100 - top_conf_percentage

                    # Display the box with scores of both classes and status
                    status = "Acc" if top_class_name == "perfect" else "Reject" if top_class_name == "defect" else ""
                    st.markdown(f"""
                    <div class="box">
                        <h2 style="color: white; text-align: center;">Result</h2>
                        <h3 style="color: white;">{top_class_name} : {top_conf_percentage:.1f}%</h3>
                        <h3 style="color: white;">Status: {status}</h3>
                    </div>
                    """, unsafe_allow_html=True)
    
                    # Create a donut chart
                    fig, ax = plt.subplots()
                    sizes = [top_conf_score, second_conf_score]
                    labels = [f'{class_name} ({conf_percentage:.1f}%)' for class_name, conf_percentage in zip([top_class_name, second_class_name], [top_conf_percentage, second_conf_percentage])]

                    # Determine colors based on prediction
                    colors = ['#66b3ff', '#ff9999'] if top_class_name == "perfect" else ['#ff9999', '#66b3ff']

                    explode = (0.1, 0) if top_class_name == "perfect" else (0, 0.1)
                    ax.pie(sizes, labels=labels, colors=colors, explode=explode, startangle=90, counterclock=False, wedgeprops={'width': 0.3, 'edgecolor': 'w'})
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

                    # Display the donut chart
                    st.pyplot(fig)



                    # Save the result to history
                    log = pd.DataFrame([{
                        "filename": file.name,
                        "class_name": top_class_name,
                        "status": status,
                        "confidence_score": f"{top_conf_percentage:.1f}%",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }])

                    # Load existing history if available
                    history_path = os.path.join(os.path.dirname(__file__), 'pages/history.csv')
                    try:
                        history = pd.read_csv(history_path)
                    except FileNotFoundError:
                        history = pd.DataFrame(columns=["filename", "class_name", "status", "confidence_score", "timestamp"])

                    # Append new log using pd.concat
                    history = pd.concat([history, log], ignore_index=True)

                    # Save updated history
                    history.to_csv(history_path, index=False)

                    # Set session state to indicate prediction is made
                    st.session_state.prediction_made = True

            # Show the reset button below the donut chart
            st.markdown('<div class="center-button">', unsafe_allow_html=True)
            if st.button('Reset'):
                if 'prediction_started' in st.session_state:
                    del st.session_state.prediction_started
                if 'prediction_made' in st.session_state:
                    del st.session_state.prediction_made
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # Sign out
    if st.sidebar.button(label='Sign Out', on_click=auth_functions.sign_out, type='primary'):
        pass
