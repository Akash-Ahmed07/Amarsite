import streamlit as st
import pandas as pd
import os
from utils.data_manager import DataManager
from utils.study_progress import StudyProgress
from utils.db_data_manager import DBDataManager
from utils.db_study_progress import DBStudyProgress
from utils.auth import Auth

# Initialize auth
if 'auth' not in st.session_state:
    st.session_state.auth = Auth()

# Initialize data manager and study progress based on authentication
auth = st.session_state.auth

if auth.is_authenticated():
    user = auth.get_current_user()
    
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

# Page configuration
st.set_page_config(
    page_title="Amarsite.Online - Study Platform",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Quizlet-inspired styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #6366f1;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .feature-card {
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
    }
    .stats-card {
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        text-align: center;
        background-color: #f8fafc;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">📚 Amarsite.Online</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Master whatever you\'re learning with interactive flashcards, practice tests and study activities.</p>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("Navigation")

auth = st.session_state.auth

if auth.is_authenticated():
    user = auth.get_current_user()
    st.sidebar.markdown(f"### 👤 {user['username']}")
    st.sidebar.markdown(f"*{user['email']}*")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        auth.logout()
        st.rerun()
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Home", "Create Study Set", "Browse Sets", "Study Mode", "Practice Test", "Spaced Review", "Public Library"]
    )
else:
    st.sidebar.info("Login to save your progress and access all features!")
    
    if st.sidebar.button("🔐 Login / Sign Up", use_container_width=True):
        st.session_state.page = "Login"
        st.rerun()
    
    page = "Login"

# Main content based on selected page
if page == "Home":
    # Welcome message and statistics
    col1, col2, col3, col4 = st.columns(4)
    
    total_sets = len(st.session_state.data_manager.get_all_sets())
    total_cards = sum(len(study_set['cards']) for study_set in st.session_state.data_manager.get_all_sets().values())
    mastered_cards = st.session_state.study_progress.get_total_mastered()
    learning_cards = st.session_state.study_progress.get_total_learning()
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3 style="color: #6366f1; margin: 0;">Study Sets</h3>
            <h2 style="margin: 0;">{total_sets}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3 style="color: #6366f1; margin: 0;">Total Cards</h3>
            <h2 style="margin: 0;">{total_cards}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <h3 style="color: #10b981; margin: 0;">Mastered</h3>
            <h2 style="margin: 0;">{mastered_cards}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3 style="color: #f59e0b; margin: 0;">Learning</h3>
            <h2 style="margin: 0;">{learning_cards}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Feature showcase
    st.subheader("🚀 How do you want to study?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Create Study Set", use_container_width=True):
            st.session_state.page = "Create Study Set"
            st.rerun()
        
        if st.button("🎯 Practice Test", use_container_width=True):
            st.session_state.page = "Practice Test"
            st.rerun()
    
    with col2:
        if st.button("📖 Browse Sets", use_container_width=True):
            st.session_state.page = "Browse Sets"
            st.rerun()
        
        if st.button("🧠 Study Mode", use_container_width=True):
            st.session_state.page = "Study Mode"
            st.rerun()
    
    # Recent activity
    if total_sets > 0:
        st.markdown("---")
        st.subheader("📊 Your Recent Study Sets")
        
        recent_sets = list(st.session_state.data_manager.get_all_sets().items())[:3]
        for set_id, study_set in recent_sets:
            with st.expander(f"📚 {study_set['title']} ({len(study_set['cards'])} cards)"):
                st.write(f"**Description:** {study_set.get('description', 'No description')}")
                st.write(f"**Created:** {study_set.get('created_date', 'Unknown')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Study {study_set['title']}", key=f"study_{set_id}"):
                        st.session_state.selected_set_id = set_id
                        st.session_state.page = "Study Mode"
                        st.rerun()
                
                with col2:
                    if st.button(f"Test {study_set['title']}", key=f"test_{set_id}"):
                        st.session_state.selected_set_id = set_id
                        st.session_state.page = "Practice Test"
                        st.rerun()

elif page == "Create Study Set":
    exec(open("pages/create_set.py").read())

elif page == "Browse Sets":
    exec(open("pages/browse_sets.py").read())

elif page == "Study Mode":
    exec(open("pages/study_mode.py").read())

elif page == "Practice Test":
    exec(open("pages/practice_test.py").read())

elif page == "Spaced Review":
    exec(open("pages/spaced_review.py").read())

elif page == "Login":
    exec(open("pages/auth.py").read())

elif page == "Public Library":
    if auth.is_authenticated():
        st.info("Public Library feature coming soon!")
    else:
        st.warning("Please login to access the Public Library")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b;'>"
    "© 2025 Amarsite.Online - Master whatever you're learning"
    "</div>", 
    unsafe_allow_html=True
)
