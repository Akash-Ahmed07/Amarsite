import streamlit as st
import uuid
from datetime import datetime
from utils.session_utils import ensure_session

ensure_session()

st.title("📝 Create Study Set")
st.markdown("Build your own flashcard set to study any subject.")

# Form for creating a new study set
with st.form("create_set_form"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        title = st.text_input("Study Set Title *", placeholder="e.g., Spanish Vocabulary")
        description = st.text_area("Description", placeholder="Describe what this study set covers...")
    
    with col2:
        subject = st.selectbox("Subject", [
            "Language Learning", "Science", "Mathematics", "History", 
            "Literature", "Business", "Medicine", "Technology", "Other"
        ])
        privacy = st.selectbox("Privacy", ["Private", "Public"])

    st.markdown("### 📚 Flashcards")
    st.markdown("Add terms and definitions for your study set:")
    
    # Initialize cards in session state if not exists
    if 'new_cards' not in st.session_state:
        st.session_state.new_cards = [{"term": "", "definition": ""}]
    
    # Display existing cards
    for i, card in enumerate(st.session_state.new_cards):
        col1, col2, col3 = st.columns([5, 5, 1])
        
        with col1:
            term = st.text_input(f"Term {i+1}", value=card["term"], key=f"term_{i}")
        
        with col2:
            definition = st.text_area(f"Definition {i+1}", value=card["definition"], key=f"def_{i}", height=100)
        
        with col3:
            if len(st.session_state.new_cards) > 1:
                if st.button("🗑️", key=f"delete_{i}", help="Delete this card"):
                    st.session_state.new_cards.pop(i)
                    st.rerun()
        
        # Update card data
        st.session_state.new_cards[i] = {"term": term, "definition": definition}
    
    # Add new card button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.form_submit_button("➕ Add Card", use_container_width=True):
            st.session_state.new_cards.append({"term": "", "definition": ""})
            st.rerun()
    
    # Form submission
    submitted = st.form_submit_button("🚀 Create Study Set", use_container_width=True)
    
    if submitted:
        if not title.strip():
            st.error("Please enter a title for your study set.")
        else:
            # Filter out empty cards
            valid_cards = [
                card for card in st.session_state.new_cards 
                if card["term"].strip() and card["definition"].strip()
            ]
            
            if len(valid_cards) == 0:
                st.error("Please add at least one complete flashcard (both term and definition).")
            else:
                # Create the study set
                set_id = str(uuid.uuid4())
                study_set = {
                    "id": set_id,
                    "title": title.strip(),
                    "description": description.strip(),
                    "subject": subject,
                    "privacy": privacy,
                    "cards": valid_cards,
                    "created_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "card_count": len(valid_cards)
                }
                
                # Save the study set
                st.session_state.data_manager.save_study_set(set_id, study_set)
                
                # Reset form
                st.session_state.new_cards = [{"term": "", "definition": ""}]
                
                st.success(f"✅ Study set '{title}' created successfully with {len(valid_cards)} cards!")
                
                # Option to start studying immediately
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📖 Start Studying", use_container_width=True):
                        st.session_state.selected_set_id = set_id
                        st.session_state.page = "Study Mode"
                        st.rerun()
                
                with col2:
                    if st.button("🎯 Take Practice Test", use_container_width=True):
                        st.session_state.selected_set_id = set_id
                        st.session_state.page = "Practice Test"
                        st.rerun()

# Quick tips
st.markdown("---")
st.markdown("### 💡 Tips for Creating Great Study Sets")
st.markdown("""
- **Be specific**: Use clear, concise terms and definitions
- **Add context**: Include examples in definitions when helpful
- **Use images**: Describe visual elements in definitions for better memory
- **Keep it focused**: Create separate sets for different topics
- **Review regularly**: Update and refine your sets as you learn
""")
