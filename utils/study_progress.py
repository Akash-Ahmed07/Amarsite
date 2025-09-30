import json
import os
from typing import Dict, List
from datetime import datetime

class StudyProgress:
    """Tracks study progress for cards and sets"""
    
    def __init__(self, progress_file: str = "study_progress.json"):
        self.progress_file = progress_file
        self.progress_data = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress data from JSON file"""
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_progress(self) -> bool:
        """Save progress data to JSON file"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving progress: {e}")
            return False
    
    def update_card_difficulty(self, set_id: str, card_index: int, difficulty: str) -> bool:
        """Update the difficulty rating for a specific card
        
        Args:
            set_id: Study set ID
            card_index: Index of the card in the set
            difficulty: 'easy', 'good', or 'hard'
        """
        if set_id not in self.progress_data:
            self.progress_data[set_id] = {}
        
        card_key = str(card_index)
        if card_key not in self.progress_data[set_id]:
            self.progress_data[set_id][card_key] = {
                'difficulty_history': [],
                'times_studied': 0,
                'last_studied': None,
                'mastery_level': 0
            }
        
        card_progress = self.progress_data[set_id][card_key]
        
        # Update difficulty history
        card_progress['difficulty_history'].append({
            'difficulty': difficulty,
            'timestamp': datetime.now().isoformat()
        })
        
        # Increment study count
        card_progress['times_studied'] += 1
        card_progress['last_studied'] = datetime.now().isoformat()
        
        # Update mastery level based on difficulty
        if difficulty == 'easy':
            card_progress['mastery_level'] = min(card_progress['mastery_level'] + 2, 10)
        elif difficulty == 'good':
            card_progress['mastery_level'] = min(card_progress['mastery_level'] + 1, 10)
        else:  # hard
            card_progress['mastery_level'] = max(card_progress['mastery_level'] - 1, 0)
        
        return self._save_progress()
    
    def get_card_progress(self, set_id: str, card_index: int) -> Dict:
        """Get progress data for a specific card"""
        card_key = str(card_index)
        
        if (set_id in self.progress_data and 
            card_key in self.progress_data[set_id]):
            return self.progress_data[set_id][card_key]
        
        return {
            'difficulty_history': [],
            'times_studied': 0,
            'last_studied': None,
            'mastery_level': 0
        }
    
    def get_set_progress(self, set_id: str) -> Dict:
        """Get overall progress for a study set"""
        if set_id not in self.progress_data:
            return {
                'studied': 0,
                'mastered': 0,
                'learning': 0,
                'difficult': 0
            }
        
        set_data = self.progress_data[set_id]
        studied = len(set_data)
        mastered = sum(1 for card in set_data.values() if card['mastery_level'] >= 8)
        learning = sum(1 for card in set_data.values() if 3 <= card['mastery_level'] < 8)
        difficult = sum(1 for card in set_data.values() if card['mastery_level'] < 3)
        
        return {
            'studied': studied,
            'mastered': mastered,
            'learning': learning,
            'difficult': difficult
        }
    
    def get_cards_by_difficulty(self, set_id: str) -> Dict[str, List[int]]:
        """Get card indices grouped by difficulty level"""
        if set_id not in self.progress_data:
            return {'easy': [], 'learning': [], 'difficult': []}
        
        easy_cards = []
        learning_cards = []
        difficult_cards = []
        
        for card_index, card_progress in self.progress_data[set_id].items():
            mastery = card_progress['mastery_level']
            card_idx = int(card_index)
            
            if mastery >= 8:
                easy_cards.append(card_idx)
            elif mastery >= 3:
                learning_cards.append(card_idx)
            else:
                difficult_cards.append(card_idx)
        
        return {
            'easy': easy_cards,
            'learning': learning_cards,
            'difficult': difficult_cards
        }
    
    def get_study_streak(self, set_id: str) -> int:
        """Calculate study streak for a set (consecutive days studied)"""
        if set_id not in self.progress_data:
            return 0
        
        # Get all study dates
        study_dates = []
        for card_progress in self.progress_data[set_id].values():
            if card_progress['last_studied']:
                try:
                    date = datetime.fromisoformat(card_progress['last_studied']).date()
                    study_dates.append(date)
                except ValueError:
                    continue
        
        if not study_dates:
            return 0
        
        # Count consecutive days
        study_dates = sorted(set(study_dates), reverse=True)
        streak = 0
        current_date = datetime.now().date()
        
        for date in study_dates:
            if (current_date - date).days == streak:
                streak += 1
            else:
                break
        
        return streak
    
    def get_total_mastered(self) -> int:
        """Get total number of mastered cards across all sets"""
        total = 0
        for set_data in self.progress_data.values():
            total += sum(1 for card in set_data.values() if card['mastery_level'] >= 8)
        return total
    
    def get_total_learning(self) -> int:
        """Get total number of cards being learned across all sets"""
        total = 0
        for set_data in self.progress_data.values():
            total += sum(1 for card in set_data.values() if 3 <= card['mastery_level'] < 8)
        return total
    
    def get_study_statistics(self) -> Dict:
        """Get comprehensive study statistics"""
        total_cards_studied = 0
        total_study_sessions = 0
        
        for set_data in self.progress_data.values():
            total_cards_studied += len(set_data)
            total_study_sessions += sum(card['times_studied'] for card in set_data.values())
        
        return {
            'total_cards_studied': total_cards_studied,
            'total_study_sessions': total_study_sessions,
            'total_mastered': self.get_total_mastered(),
            'total_learning': self.get_total_learning(),
            'sets_with_progress': len(self.progress_data)
        }
