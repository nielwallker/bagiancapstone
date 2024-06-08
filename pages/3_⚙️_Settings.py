import streamlit as st
import auth_functions

# Function to check if user is logged in
def is_user_logged_in():
    return 'user_info' in st.session_state

# Authentication required for page access
if not is_user_logged_in():
    st.warning("You must be logged in to view this page.")
else:
    # Delete Account
    #st.header('Delete account:')
    #password = st.text_input(label='Confirm your password', type='password')
    #if st.button(label='Delete Account'):
     #   auth_functions.delete_account(password)
    
    # Change Password
    st.header('Change Password:')
    email = st.text_input(label='Email')
    old_password = st.text_input(label='Old Password', type='password')
    new_password = st.text_input(label='New Password', type='password')
    confirm_new_password = st.text_input(label='Confirm New Password', type='password')
    
    if st.button('Change Password'):
        if new_password == confirm_new_password:
            auth_functions.change_password(email, old_password, new_password)
            st.success('Password changed successfully.')
        else:
            st.error("New password and confirm new password must match.")
