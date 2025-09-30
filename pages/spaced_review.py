import streamlit as st
from utils.spaced_repetition import SpacedRepetition
from datetime import datetime

st.title("📅 Spaced Repetition Review")
st.markdown("Review cards that are due based on the spaced repetition algorithm for optimal learning.")

# Check authentication
auth = st.session_state.auth
if not auth.is_authenticated():
    st.warning("Please login to use spaced repetition review.")
    if st.button("🔐 Login"):
        st.session_state.page = "Login"
        st.rerun()
    st.stop()

user = auth.get_current_user()

# Get all study sets
all_sets = st.session_state.data_manager.get_all_sets()

if not all_sets:
    st.info("You don't have any study sets yet. Create one to start learning!")
    if st.button("📝 Create Study Set"):
        st.session_state.page = "Create Study Set"
        st.rerun()
    st.stop()

# Calculate due cards for each set
due_cards_by_set = {}
total_due = 0

for set_id, study_set in all_sets.items():
    cards = study_set.get('cards', [])
    if not cards:
        continue
    
    due_cards = []
    for i in range(len(cards)):
        progress = st.session_state.study_progress.get_card_progress(set_id, i)
        next_review = progress.get('next_review_date')
        
        if next_review is None:
            due_cards.append(i)
        else:
            if isinstance(next_review, str):
                try:
                    next_review_dt = datetime.fromisoformat(next_review)
                    if SpacedRepetition.is_due_for_review(next_review_dt):
                        due_cards.append(i)
                except:
                    due_cards.append(i)
            elif isinstance(next_review, datetime):
                if SpacedRepetition.is_due_for_review(next_review):
                    due_cards.append(i)
    
    if due_cards:
        due_cards_by_set[set_id] = {
            'title': study_set['title'],
            'due_cards': due_cards,
            'total_cards': len(cards)
        }
        total_due += len(due_cards)

# Display summary
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📚 Total Sets", len(all_sets))

with col2:
    st.metric("📅 Sets with Due Cards", len(due_cards_by_set))

with col3:
    st.metric("🔔 Total Due Cards", total_due)

st.markdown("---")

if not due_cards_by_set:
    st.success("🎉 Great job! You're all caught up on your reviews!")
    st.info("Come back later when cards are due for review based on your performance.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 Browse All Sets", use_container_width=True):
            st.session_state.page = "Browse Sets"
            st.rerun()
    with col2:
        if st.button("🏠 Go Home", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()
else:
    st.subheader(f"📚 Study Sets with Due Reviews ({len(due_cards_by_set)})")
    
    for set_id, set_info in due_cards_by_set.items():
        with st.container():
            st.markdown(f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin: 1rem 0; background-color: #f8fafc;">
                <h4 style="color: #6366f1; margin-top: 0;">{set_info['title']}</h4>
                <p style="color: #64748b;">
                    <strong>{len(set_info['due_cards'])}</strong> cards due for review out of {set_info['total_cards']} total
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"📖 Review {set_info['title']}", key=f"review_{set_id}", use_container_width=True):
                    st.session_state.selected_set_id = set_id
                    st.session_state.spaced_review_mode = True
                    st.session_state.spaced_due_cards = set_info['due_cards']
                    st.session_state.page = "Study Mode"
                    st.rerun()
            
            with col2:
                if st.button(f"📊 View Progress", key=f"progress_{set_id}", use_container_width=True):
                    progress_data = st.session_state.study_progress.get_set_progress(set_id)
                    
                    with st.expander(f"Progress for {set_info['title']}", expanded=True):
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Mastered", progress_data['mastered'])
                        with col_b:
                            st.metric("Learning", progress_data['learning'])
                        with col_c:
                            st.metric("Difficult", progress_data['difficult'])
                        
                        mastery_pct = (progress_data['mastered'] / set_info['total_cards'] * 100) if set_info['total_cards'] > 0 else 0
                        st.progress(mastery_pct / 100)
                        st.caption(f"{mastery_pct:.1f}% mastery")

st.markdown("---")
st.markdown("### 💡 About Spaced Repetition")
st.markdown("""
Spaced repetition is a scientifically proven learning technique that helps you remember information longer by reviewing it at optimal intervals:

- **New cards**: Review frequently (within hours)
- **Learning cards**: Review daily
- **Young cards**: Review weekly  
- **Mature cards**: Review monthly
- **Mastered cards**: Review every few months

The system automatically schedules your reviews based on how well you know each card!
""")
