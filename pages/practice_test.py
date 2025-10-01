import streamlit as st
import random
from utils.session_utils import ensure_session

ensure_session()

st.title("🎯 Practice Test")

# Check if a study set is selected
if 'selected_set_id' not in st.session_state:
    st.warning("Please select a study set for practice test.")
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

st.markdown(f"**Testing:** {study_set['title']}")

# Test configuration
if 'test_session' not in st.session_state or st.button("🔄 Start New Test"):
    st.markdown("### 🛠️ Test Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        test_type = st.selectbox("Test Type", ["Multiple Choice", "Written Response", "Mixed"])
        num_questions = st.slider("Number of Questions", 1, min(len(study_set['cards']), 20), min(10, len(study_set['cards'])))
    
    with col2:
        question_order = st.selectbox("Question Order", ["Random", "Original Order"])
        time_limit = st.selectbox("Time Limit", ["No Limit", "1 minute per question", "30 seconds per question"])
    
    if st.button("🚀 Start Test", use_container_width=True):
        # Create test questions
        test_cards = study_set['cards'].copy()
        if question_order == "Random":
            random.shuffle(test_cards)
        
        test_cards = test_cards[:num_questions]
        questions = []
        
        for i, card in enumerate(test_cards):
            if test_type == "Multiple Choice" or (test_type == "Mixed" and random.choice([True, False])):
                # Create multiple choice question
                question = {
                    'type': 'multiple_choice',
                    'question': f"What is the definition of: {card['term']}?",
                    'correct_answer': card['definition'],
                    'options': []
                }
                
                # Add correct answer
                question['options'].append(card['definition'])
                
                # Add wrong answers from other cards
                other_cards = [c for c in study_set['cards'] if c != card]
                wrong_answers = random.sample(other_cards, min(3, len(other_cards)))
                for wrong_card in wrong_answers:
                    question['options'].append(wrong_card['definition'])
                
                random.shuffle(question['options'])
                questions.append(question)
            else:
                # Create written response question
                question = {
                    'type': 'written',
                    'question': f"Define: {card['term']}",
                    'correct_answer': card['definition'],
                    'term': card['term']
                }
                questions.append(question)
        
        st.session_state.test_session = {
            'questions': questions,
            'current_question': 0,
            'answers': [],
            'score': 0,
            'started': True,
            'completed': False,
            'start_time': st.session_state.get('current_time', 0)
        }
        st.rerun()

# Test execution
if 'test_session' in st.session_state and st.session_state.test_session.get('started', False):
    test_session = st.session_state.test_session
    
    if not test_session.get('completed', False):
        questions = test_session['questions']
        current_q = test_session['current_question']
        
        if current_q < len(questions):
            question = questions[current_q]
            
            # Progress indicator
            progress = (current_q + 1) / len(questions)
            st.progress(progress)
            st.markdown(f"**Question {current_q + 1} of {len(questions)}**")
            
            # Display question
            st.markdown(f"### {question['question']}")
            
            if question['type'] == 'multiple_choice':
                # Multiple choice question
                answer = st.radio(
                    "Select the correct answer:",
                    question['options'],
                    key=f"q_{current_q}"
                )
                
                if st.button("Submit Answer", key=f"submit_{current_q}"):
                    is_correct = answer == question['correct_answer']
                    test_session['answers'].append({
                        'question': question['question'],
                        'user_answer': answer,
                        'correct_answer': question['correct_answer'],
                        'is_correct': is_correct
                    })
                    
                    if is_correct:
                        test_session['score'] += 1
                        st.success("✅ Correct!")
                    else:
                        st.error(f"❌ Incorrect. The correct answer is: {question['correct_answer']}")
                    
                    test_session['current_question'] += 1
                    
                    if test_session['current_question'] >= len(questions):
                        test_session['completed'] = True
                    
                    st.rerun()
            
            else:
                # Written response question
                user_answer = st.text_area(
                    "Your answer:",
                    key=f"written_{current_q}",
                    height=100
                )
                
                if st.button("Submit Answer", key=f"submit_written_{current_q}"):
                    # Simple similarity check (case-insensitive)
                    correct_answer = question['correct_answer'].lower().strip()
                    user_answer_clean = user_answer.lower().strip()
                    
                    # Basic scoring - check if key words are present
                    correct_words = set(correct_answer.split())
                    user_words = set(user_answer_clean.split())
                    overlap = len(correct_words.intersection(user_words))
                    similarity = overlap / len(correct_words) if correct_words else 0
                    
                    is_correct = similarity >= 0.6  # 60% word overlap threshold
                    
                    test_session['answers'].append({
                        'question': question['question'],
                        'user_answer': user_answer,
                        'correct_answer': question['correct_answer'],
                        'is_correct': is_correct,
                        'similarity': similarity
                    })
                    
                    if is_correct:
                        test_session['score'] += 1
                        st.success("✅ Good answer!")
                    else:
                        st.warning(f"⚠️ Your answer needs improvement. Expected: {question['correct_answer']}")
                    
                    # Show comparison
                    st.markdown("**Your answer:**")
                    st.write(user_answer)
                    st.markdown("**Expected answer:**")
                    st.write(question['correct_answer'])
                    
                    test_session['current_question'] += 1
                    
                    if test_session['current_question'] >= len(questions):
                        test_session['completed'] = True
                    
                    st.rerun()
        
    else:
        # Test completed - show results
        st.success("🎉 Test Completed!")
        
        score_percentage = (test_session['score'] / len(test_session['questions'])) * 100
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Score", f"{test_session['score']}/{len(test_session['questions'])}")
        
        with col2:
            st.metric("Percentage", f"{score_percentage:.1f}%")
        
        with col3:
            if score_percentage >= 80:
                grade = "A"
                color = "🟢"
            elif score_percentage >= 70:
                grade = "B"
                color = "🟡"
            elif score_percentage >= 60:
                grade = "C"
                color = "🟠"
            else:
                grade = "F"
                color = "🔴"
            
            st.metric("Grade", f"{color} {grade}")
        
        # Progress bar for score
        st.progress(score_percentage / 100)
        
        # Detailed results
        st.markdown("### 📋 Detailed Results")
        
        for i, answer in enumerate(test_session['answers']):
            with st.expander(f"Question {i+1}: {'✅' if answer['is_correct'] else '❌'}"):
                st.write(f"**Question:** {answer['question']}")
                st.write(f"**Your Answer:** {answer['user_answer']}")
                st.write(f"**Correct Answer:** {answer['correct_answer']}")
                
                if 'similarity' in answer:
                    st.write(f"**Similarity Score:** {answer['similarity']:.1%}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Retake Test"):
                del st.session_state.test_session
                st.rerun()
        
        with col2:
            if st.button("📖 Study More"):
                st.session_state.page = "Study Mode"
                st.rerun()
        
        with col3:
            if st.button("📊 Browse Sets"):
                st.session_state.page = "Browse Sets"
                st.rerun()
        
        # Update study progress based on test results
        for answer in test_session['answers']:
            if answer['is_correct']:
                # Mark as mastered if answered correctly
                # Find the card index for this question
                for card_idx, card in enumerate(study_set['cards']):
                    if card['term'] in answer['question']:
                        st.session_state.study_progress.update_card_difficulty(
                            st.session_state.selected_set_id, card_idx, 'easy'
                        )
                        break

# Sidebar with test statistics
if 'test_session' in st.session_state and st.session_state.test_session.get('started', False):
    with st.sidebar:
        st.markdown("### 🎯 Test Progress")
        
        test_session = st.session_state.test_session
        
        if not test_session.get('completed', False):
            st.metric("Questions Completed", f"{test_session['current_question']}/{len(test_session['questions'])}")
            st.metric("Current Score", f"{test_session['score']}/{test_session['current_question']}" if test_session['current_question'] > 0 else "0/0")
        
        if test_session['current_question'] > 0:
            current_percentage = (test_session['score'] / test_session['current_question']) * 100
            st.progress(current_percentage / 100)
            st.caption(f"{current_percentage:.1f}% Correct So Far")
