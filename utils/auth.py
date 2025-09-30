import bcrypt
import streamlit as st
from utils.db import Database
from typing import Optional, Dict

class Auth:
    """Authentication handler for Amarsite.Online"""
    
    def __init__(self):
        self.db = Database()
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def register_user(self, username: str, email: str, password: str) -> tuple[bool, str]:
        """Register a new user"""
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if '@' not in email:
            return False, "Invalid email address"
        
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return False, "Username already exists"
        
        existing_email = self.db.get_user_by_email(email)
        if existing_email:
            return False, "Email already registered"
        
        password_hash = self.hash_password(password)
        
        try:
            user_id = self.db.create_user(username, email, password_hash)
            if user_id:
                return True, "Account created successfully"
            else:
                return False, "Failed to create account"
        except Exception as e:
            return False, f"Error creating account: {str(e)}"
    
    def login_user(self, username: str, password: str) -> tuple[bool, str, Optional[Dict]]:
        """Login a user"""
        user = self.db.get_user_by_username(username)
        
        if not user:
            return False, "Invalid username or password", None
        
        user_id, db_username, email, password_hash = user
        
        if self.verify_password(password, password_hash):
            self.db.update_last_login(user_id)
            
            user_data = {
                'id': user_id,
                'username': db_username,
                'email': email
            }
            
            return True, "Login successful", user_data
        else:
            return False, "Invalid username or password", None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'user' in st.session_state and st.session_state.user is not None
    
    def get_current_user(self) -> Optional[Dict]:
        """Get current logged in user"""
        return st.session_state.get('user')
    
    def logout(self):
        """Logout current user"""
        if 'user' in st.session_state:
            del st.session_state.user
        
        keys_to_remove = ['selected_set_id', 'study_session', 'test_session', 'new_cards']
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def require_auth(self):
        """Decorator-like function to require authentication"""
        if not self.is_authenticated():
            st.warning("Please log in to access this feature")
            st.stop()
