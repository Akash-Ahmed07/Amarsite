import streamlit as st
from utils.session_utils import ensure_session

ensure_session()

st.title("🌐 Public Library")
st.markdown("Discover and copy study sets shared by other users")

if not st.session_state.auth.is_authenticated():
    st.warning("Please log in to access the Public Library and copy study sets")
    st.stop()

db = st.session_state.db
user_id = st.session_state.user_id

# Search and filter
col1, col2 = st.columns([3, 1])

with col1:
    search_term = st.text_input("🔍 Search public study sets", placeholder="Search by title, description, or author...")

with col2:
    sort_by = st.selectbox("Sort by", ["Recently Created", "Most Cards", "Title (A-Z)"])

# Get public study sets
public_sets = db.get_public_study_sets(limit=100)

if not public_sets:
    st.info("No public study sets available yet. Be the first to share!")
    st.stop()

# Filter by search term
filtered_sets = []
for study_set in public_sets:
    if search_term:
        search_lower = search_term.lower()
        if (search_lower not in study_set['title'].lower() and 
            search_lower not in study_set.get('description', '').lower() and
            search_lower not in study_set.get('author', '').lower()):
            continue
    filtered_sets.append(study_set)

# Sort sets
if sort_by == "Recently Created":
    filtered_sets.sort(key=lambda x: x.get('created_at', ''), reverse=True)
elif sort_by == "Most Cards":
    filtered_sets.sort(key=lambda x: x.get('card_count', 0), reverse=True)
else:  # Title (A-Z)
    filtered_sets.sort(key=lambda x: x['title'].lower())

st.markdown(f"**{len(filtered_sets)}** public study sets found")
st.markdown("---")

# Display public study sets in a grid
for i in range(0, len(filtered_sets), 2):
    cols = st.columns(2)
    
    for j, col in enumerate(cols):
        if i + j < len(filtered_sets):
            study_set = filtered_sets[i + j]
            
            with col:
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; background-color: #f8fafc;">
                        <h4 style="color: #6366f1; margin-top: 0;">{study_set['title']}</h4>
                        <p style="color: #64748b; font-size: 0.9rem;">{study_set.get('description', 'No description')[:100]}{'...' if len(study_set.get('description', '')) > 100 else ''}</p>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                            <span style="background-color: #6366f1; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">{study_set.get('card_count', 0)} cards</span>
                            <span style="color: #64748b; font-size: 0.8rem;">{study_set.get('subject', 'Other')}</span>
                        </div>
                        <div style="margin-top: 0.5rem;">
                            <span style="color: #64748b; font-size: 0.75rem;">by {study_set.get('author', 'Anonymous')}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        if st.button("👁️ Preview", key=f"preview_{study_set['id']}", use_container_width=True):
                            st.session_state.preview_set_id = study_set['id']
                            st.rerun()
                    
                    with col_b:
                        if st.button("📥 Copy to My Sets", key=f"copy_{study_set['id']}", use_container_width=True):
                            new_set_id = db.copy_study_set(study_set['id'], user_id)
                            if new_set_id:
                                st.success(f"✅ Copied '{study_set['title']}' to your collection!")
                                st.balloons()
                            else:
                                st.error("Failed to copy study set")

# Preview modal
if hasattr(st.session_state, 'preview_set_id') and st.session_state.preview_set_id:
    preview_set_id = st.session_state.preview_set_id
    preview_set = db.get_study_set(preview_set_id)
    
    if preview_set:
        with st.expander(f"👁️ Preview: {preview_set['title']}", expanded=True):
            st.markdown(f"**Description:** {preview_set.get('description', 'No description')}")
            st.markdown(f"**Subject:** {preview_set.get('subject', 'Other')}")
            
            cards = db.get_cards(preview_set_id)
            st.markdown(f"**Total Cards:** {len(cards)}")
            
            st.markdown("---")
            st.markdown("### Preview Cards")
            
            for i, card in enumerate(cards[:10]):
                with st.expander(f"Card {i+1}: {card['term'][:50]}"):
                    st.write(f"**Term:** {card['term']}")
                    st.write(f"**Definition:** {card['definition']}")
            
            if len(cards) > 10:
                st.caption(f"... and {len(cards) - 10} more cards")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📥 Copy to My Sets", key=f"copy_preview_{preview_set_id}"):
                    new_set_id = db.copy_study_set(preview_set_id, user_id)
                    if new_set_id:
                        st.success(f"✅ Copied '{preview_set['title']}' to your collection!")
                        del st.session_state.preview_set_id
                        st.balloons()
                        st.rerun()
            
            with col2:
                if st.button("Close", key=f"close_preview_{preview_set_id}"):
                    del st.session_state.preview_set_id
                    st.rerun()
