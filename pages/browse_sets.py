import streamlit as st
from utils import auth

st.title("📖 Browse Study Sets")
st.markdown("Explore and manage your study sets.")

# Handle sharing modal
if hasattr(st.session_state, 'sharing_set_id') and st.session_state.sharing_set_id:
    sharing_set_id = st.session_state.sharing_set_id
    sharing_set = st.session_state.data_manager.get_study_set(sharing_set_id)
    
    if sharing_set:
        with st.expander(f"🔗 Share: {sharing_set['title']}", expanded=True):
            st.markdown("### Sharing Settings")
            
            # Get current sharing settings
            is_authenticated = auth.is_authenticated()
            
            if is_authenticated:
                db = st.session_state.db
                user_id = st.session_state.user_id
                
                # Get current share code
                set_data = db.get_study_set(sharing_set_id)
                current_share_code = set_data.get('share_code') if set_data else None
                
                # Public/Private toggle
                is_public = set_data.get('is_public', False) if set_data else False
                new_is_public = st.toggle("Make this set public", value=is_public, key=f"public_toggle_{sharing_set_id}")
                
                if new_is_public != is_public:
                    db.update_study_set(sharing_set_id, user_id, is_public=new_is_public)
                    st.success("✅ Visibility updated!")
                    st.rerun()
                
                st.markdown("---")
                st.markdown("### Share Link")
                
                if current_share_code:
                    share_url = f"https://{st.session_state.get('REPL_SLUG', 'amarsite-online')}.replit.app?share={current_share_code}"
                    st.code(share_url, language=None)
                    st.caption("Anyone with this link can view and copy this study set")
                else:
                    if st.button("Generate Share Link", key=f"gen_share_{sharing_set_id}"):
                        share_code = db.generate_share_code(sharing_set_id, user_id)
                        st.success("✅ Share link generated!")
                        st.rerun()
                
                if st.button("Close", key=f"close_share_{sharing_set_id}"):
                    del st.session_state.sharing_set_id
                    st.rerun()
            else:
                st.warning("Please log in to share study sets")
                if st.button("Close", key=f"close_share_anon_{sharing_set_id}"):
                    del st.session_state.sharing_set_id
                    st.rerun()

# Get all study sets
all_sets = st.session_state.data_manager.get_all_sets()

if not all_sets:
    st.info("No study sets found. Create your first study set to get started!")
    if st.button("📝 Create Study Set"):
        st.session_state.page = "Create Study Set"
        st.rerun()
else:
    # Search and filter options
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search study sets", placeholder="Search by title or description...")
    
    with col2:
        subjects = ["All"] + list(set(study_set.get('subject', 'Other') for study_set in all_sets.values()))
        selected_subject = st.selectbox("Subject Filter", subjects)
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Recently Created", "Title (A-Z)", "Card Count"])
    
    # Filter sets based on search and subject
    filtered_sets = {}
    for set_id, study_set in all_sets.items():
        # Search filter
        if search_term:
            if (search_term.lower() not in study_set['title'].lower() and 
                search_term.lower() not in study_set.get('description', '').lower()):
                continue
        
        # Subject filter
        if selected_subject != "All" and study_set.get('subject', 'Other') != selected_subject:
            continue
        
        filtered_sets[set_id] = study_set
    
    # Sort sets
    if sort_by == "Recently Created":
        sorted_sets = sorted(filtered_sets.items(), key=lambda x: x[1].get('created_date', ''), reverse=True)
    elif sort_by == "Title (A-Z)":
        sorted_sets = sorted(filtered_sets.items(), key=lambda x: x[1]['title'].lower())
    else:  # Card Count
        sorted_sets = sorted(filtered_sets.items(), key=lambda x: len(x[1]['cards']), reverse=True)
    
    st.markdown(f"**{len(filtered_sets)}** study sets found")
    
    # Display study sets in a grid
    for i in range(0, len(sorted_sets), 2):
        cols = st.columns(2)
        
        for j, col in enumerate(cols):
            if i + j < len(sorted_sets):
                set_id, study_set = sorted_sets[i + j]
                
                with col:
                    with st.container():
                        st.markdown(f"""
                        <div style="border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; background-color: #f8fafc;">
                            <h4 style="color: #6366f1; margin-top: 0;">{study_set['title']}</h4>
                            <p style="color: #64748b; font-size: 0.9rem;">{study_set.get('description', 'No description')[:100]}{'...' if len(study_set.get('description', '')) > 100 else ''}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                                <span style="background-color: #6366f1; color: white; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">{len(study_set['cards'])} cards</span>
                                <span style="color: #64748b; font-size: 0.8rem;">{study_set.get('subject', 'Other')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Action buttons
                        col_a, col_b, col_c, col_d = st.columns(4)
                        
                        with col_a:
                            if st.button("📖 Study", key=f"study_{set_id}", use_container_width=True):
                                st.session_state.selected_set_id = set_id
                                st.session_state.page = "Study Mode"
                                st.rerun()
                        
                        with col_b:
                            if st.button("🎯 Test", key=f"test_{set_id}", use_container_width=True):
                                st.session_state.selected_set_id = set_id
                                st.session_state.page = "Practice Test"
                                st.rerun()
                        
                        with col_c:
                            if st.button("🔗 Share", key=f"share_{set_id}", use_container_width=True):
                                st.session_state.sharing_set_id = set_id
                                st.rerun()
                        
                        with col_d:
                            if st.button("🗑️ Delete", key=f"delete_{set_id}", use_container_width=True):
                                if st.session_state.data_manager.delete_study_set(set_id):
                                    st.success(f"Deleted '{study_set['title']}'")
                                    st.rerun()
                        
                        # Study progress for this set
                        progress = st.session_state.study_progress.get_set_progress(set_id)
                        if progress['studied'] > 0:
                            mastery_percentage = (progress['mastered'] / len(study_set['cards'])) * 100
                            st.progress(mastery_percentage / 100)
                            st.caption(f"Progress: {progress['mastered']}/{len(study_set['cards'])} mastered ({mastery_percentage:.0f}%)")

# Summary statistics
if all_sets:
    st.markdown("---")
    st.markdown("### 📊 Your Study Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_sets = len(all_sets)
    total_cards = sum(len(study_set['cards']) for study_set in all_sets.values())
    subjects = list(set(study_set.get('subject', 'Other') for study_set in all_sets.values()))
    avg_cards = total_cards / total_sets if total_sets > 0 else 0
    
    with col1:
        st.metric("Total Sets", total_sets)
    
    with col2:
        st.metric("Total Cards", total_cards)
    
    with col3:
        st.metric("Subjects", len(subjects))
    
    with col4:
        st.metric("Avg Cards/Set", f"{avg_cards:.1f}")
