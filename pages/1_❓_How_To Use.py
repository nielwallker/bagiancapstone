import streamlit as st

# Function to check if user is logged in
def is_user_logged_in():
    return 'user_info' in st.session_state

# Authentication required for page access
if not is_user_logged_in():
    st.warning("You must be logged in to view this page.")
else:
    st.title("How To Use")
    
    st.header("Instructions")
    
    markdown = """
    1. login using the username or password that has been registered.
    2. After login, the dashboard page will appear immediately.
    3. In the dashboard section there are two views to upload an image, you can click the upload image button or drag and drop the image.
    4. After selecting and entering the image to be inspected, the system will automatically classify the image.
    5. After the image is processed, the inspection result will appear on the screen and the inspection result will show the percentage of product quality.
    6. If the inspection result is less than 95%, the product is defective and needs to be repaired.
    7. If the inspection result is 95% or more, even up to 100%, then the product passes the inspection and is ready for distribution.
    """
    
    st.markdown(markdown)


