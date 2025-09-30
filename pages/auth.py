import streamlit as st
from utils.auth import Auth

auth = Auth()

st.title("🔐 Welcome to Amarsite.Online")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.subheader("Login to Your Account")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, message, user_data = auth.login_user(username, password)
                
                if success:
                    st.session_state.user = user_data
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with tab2:
    st.subheader("Create New Account")
    
    with st.form("signup_form"):
        new_username = st.text_input("Choose Username")
        new_email = st.text_input("Email Address")
        new_password = st.text_input("Choose Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
        
        if submit_signup:
            if not new_username or not new_email or not new_password:
                st.error("Please fill in all fields")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                success, message = auth.register_user(new_username, new_email, new_password)
                
                if success:
                    st.success(message + " Please login to continue.")
                else:
                    st.error(message)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b;'>"
    "New to Amarsite.Online? Sign up to save your study sets and track your progress!"
    "</div>", 
    unsafe_allow_html=True
)
