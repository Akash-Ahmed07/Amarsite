import streamlit as st
from utils.auth import Auth
from utils.data_manager import DataManager
from utils.study_progress import StudyProgress
from utils.db_data_manager import DBDataManager
from utils.db_study_progress import DBStudyProgress

def ensure_session():
    """Initialize session state with required objects"""
    if 'auth' not in st.session_state:
        st.session_state.auth = Auth()
    
    auth = st.session_state.auth
    
    if auth.is_authenticated():
        user = auth.get_current_user()
        if user:
            st.session_state.user_id = user['id']
            
            if 'db' not in st.session_state:
                from utils.db import Database
                st.session_state.db = Database()
            
            if 'db_data_manager' not in st.session_state:
                st.session_state.db_data_manager = DBDataManager(user['id'])
                st.session_state.db_study_progress = DBStudyProgress(user['id'])
            else:
                st.session_state.db_data_manager.set_user(user['id'])
                st.session_state.db_study_progress.set_user(user['id'])
            
            st.session_state.data_manager = st.session_state.db_data_manager
            st.session_state.study_progress = st.session_state.db_study_progress
    else:
        if 'json_data_manager' not in st.session_state:
            st.session_state.json_data_manager = DataManager()
            st.session_state.json_study_progress = StudyProgress()
        
        st.session_state.data_manager = st.session_state.json_data_manager
        st.session_state.study_progress = st.session_state.json_study_progress
