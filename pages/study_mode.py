import streamlit as st
import random
from utils.session_utils import ensure_session

ensure_session()

st.title("🧠 Study Mode")

# Check if a study set is selected
if 'selected_set_id' not in st.session_state:
    st.warning("Please select a study set to study.")
    st.markdown("Go to **Browse Sets** to choose a study set.")
    if st.button("📖 Browse Sets"):
        st.session_state.page = "Browse Sets"
        st.rerun()
    st.stop()

# Get the selected study set
study_set = st.session_state.data_manager.get_study_set(st.session_state.selected_set_id)
if not study_set:
    st.error("Study set not found.")
    st.stop()

st.markdown(f"**Studying:** {study_set['title']}")
st.markdown(f"*{len(study_set['cards'])} cards*")

# Initialize study session
if 'study_session' not in st.session_state:
    st.session_state.study_session = {
        'cards': study_set['cards'].copy(),
        'current_index': 0,
        'show_definition': False,
        'shuffled': False,
        'studied_cards': set(),
        'difficult_cards': [],
        'easy_cards': []
    }

cards = st.session_state.study_session['cards']
current_index = st.session_state.study_session['current_index']

if not cards:
    st.info("No cards in this study set.")
    st.stop()

# Study mode controls
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("🔀 Shuffle Cards"):
        random.shuffle(st.session_state.study_session['cards'])
        st.session_state.study_session['shuffled'] = True
        st.rerun()

with col2:
    st.markdown(f"**Card {current_index + 1} of {len(cards)}**")
    progress = (current_index + 1) / len(cards)
    st.progress(progress)

with col3:
    if st.button("🔄 Reset Session"):
        st.session_state.study_session = {
            'cards': study_set['cards'].copy(),
            'current_index': 0,
            'show_definition': False,
            'shuffled': False,
            'studied_cards': set(),
            'difficult_cards': [],
            'easy_cards': []
        }
        st.rerun()

# Current card display
current_card = cards[current_index]

# Flashcard container with flip animation simulation
with st.container():
    if not st.session_state.study_session['show_definition']:
        # Show term (front of card)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem;
            border-radius: 16px;
            text-align: center;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 2rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        ">
            {current_card['term']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if st.button("🔄 Show Definition", use_container_width=True, key="show_def"):
            st.session_state.study_session['show_definition'] = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        # Show definition (back of card)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 3rem;
            border-radius: 16px;
            text-align: center;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            margin: 2rem 0;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        ">
            {current_card['definition']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        if st.button("🔄 Show Term", use_container_width=True, key="show_term"):
            st.session_state.study_session['show_definition'] = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# Helper function to move to next card
def next_card():
    """Helper function to move to next card"""
    if st.session_state.study_session['current_index'] < len(cards) - 1:
        st.session_state.study_session['current_index'] += 1
        st.session_state.study_session['show_definition'] = False
        st.session_state.study_session['studied_cards'].add(current_index)
        st.rerun()

# Card difficulty rating (when definition is shown)
if st.session_state.study_session['show_definition']:
    st.markdown("---")
    st.markdown("**How well did you know this card?**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("😰 Hard", use_container_width=True, type="secondary"):
            st.session_state.study_session['difficult_cards'].append(current_card)
            st.session_state.study_progress.update_card_difficulty(
                st.session_state.selected_set_id, current_index, 'hard'
            )
            next_card()
    
    with col2:
        if st.button("😐 Good", use_container_width=True, type="secondary"):
            st.session_state.study_progress.update_card_difficulty(
                st.session_state.selected_set_id, current_index, 'good'
            )
            next_card()
    
    with col3:
        if st.button("😊 Easy", use_container_width=True, type="primary"):
            st.session_state.study_session['easy_cards'].append(current_card)
            st.session_state.study_progress.update_card_difficulty(
                st.session_state.selected_set_id, current_index, 'easy'
            )
            next_card()

# Navigation buttons
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Previous", disabled=(current_index == 0)):
        if current_index > 0:
            st.session_state.study_session['current_index'] -= 1
            st.session_state.study_session['show_definition'] = False
            st.rerun()

with col3:
    if st.button("➡️ Next", disabled=(current_index == len(cards) - 1)):
        if current_index < len(cards) - 1:
            st.session_state.study_session['current_index'] += 1
            st.session_state.study_session['show_definition'] = False
            st.rerun()

# Study session summary
if current_index == len(cards) - 1 and st.session_state.study_session['show_definition']:
    st.markdown("---")
    st.success("🎉 You've completed this study session!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Cards Studied", len(st.session_state.study_session['studied_cards']))
        st.metric("Easy Cards", len(st.session_state.study_session['easy_cards']))
    
    with col2:
        st.metric("Difficult Cards", len(st.session_state.study_session['difficult_cards']))
        
        if st.button("📝 Study Difficult Cards Only"):
            if st.session_state.study_session['difficult_cards']:
                st.session_state.study_session['cards'] = st.session_state.study_session['difficult_cards']
                st.session_state.study_session['current_index'] = 0
                st.session_state.study_session['show_definition'] = False
                st.rerun()

# Sidebar with study progress
with st.sidebar:
    st.markdown("### 📊 Study Progress")
    
    progress_data = st.session_state.study_progress.get_set_progress(st.session_state.selected_set_id)
    
    st.metric("Cards Mastered", f"{progress_data['mastered']}/{len(study_set['cards'])}")
    st.metric("Cards Learning", f"{progress_data['learning']}/{len(study_set['cards'])}")
    
    if len(study_set['cards']) > 0:
        mastery_percentage = (progress_data['mastered'] / len(study_set['cards'])) * 100
        st.progress(mastery_percentage / 100)
        st.caption(f"{mastery_percentage:.0f}% Mastered")
