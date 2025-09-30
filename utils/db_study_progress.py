from typing import Dict, List
from utils.db import Database
from datetime import datetime

class DBStudyProgress:
    """Database-backed study progress tracker"""
    
    def __init__(self, user_id: int = None):
        self.db = Database()
        self.user_id = user_id
    
    def set_user(self, user_id: int):
        """Set the current user ID"""
        self.user_id = user_id
    
    def update_card_difficulty(self, set_id: str, card_index: int, difficulty: str) -> bool:
        """Update the difficulty rating for a specific card"""
        if not self.user_id:
            return False
        
        study_set = self.db.get_study_set(set_id, self.user_id)
        if not study_set or card_index >= len(study_set['cards']):
            return False
        
        card_id = study_set['cards'][card_index]['id']
        
        mastery_level_map = {
            'hard': -1,
            'good': 1,
            'easy': 2
        }
        
        current_progress = self.db.execute_query(
            "SELECT mastery_level FROM study_progress WHERE user_id = %s AND card_id = %s",
            (self.user_id, card_id),
            fetch='one'
        )
        
        if current_progress:
            current_mastery = current_progress[0] or 0
        else:
            current_mastery = 0
        
        change = mastery_level_map.get(difficulty, 0)
        new_mastery = max(0, min(10, current_mastery + change))
        
        return self.db.update_study_progress(
            user_id=self.user_id,
            card_id=card_id,
            study_set_id=set_id,
            difficulty=difficulty,
            mastery_level=new_mastery
        )
    
    def get_card_progress(self, set_id: str, card_index: int) -> Dict:
        """Get progress data for a specific card"""
        if not self.user_id:
            return {
                'difficulty_history': [],
                'times_studied': 0,
                'last_studied': None,
                'mastery_level': 0
            }
        
        study_set = self.db.get_study_set(set_id, self.user_id)
        if not study_set or card_index >= len(study_set['cards']):
            return {
                'difficulty_history': [],
                'times_studied': 0,
                'last_studied': None,
                'mastery_level': 0
            }
        
        card_id = study_set['cards'][card_index]['id']
        
        progress = self.db.execute_query(
            """SELECT mastery_level, times_studied, last_studied, difficulty_history 
               FROM study_progress WHERE user_id = %s AND card_id = %s""",
            (self.user_id, card_id),
            fetch='one'
        )
        
        if progress:
            import json
            difficulty_history = progress[3]
            if isinstance(difficulty_history, str):
                difficulty_history = json.loads(difficulty_history)
            elif not isinstance(difficulty_history, list):
                difficulty_history = []
            
            return {
                'mastery_level': progress[0] or 0,
                'times_studied': progress[1] or 0,
                'last_studied': progress[2].isoformat() if progress[2] else None,
                'difficulty_history': difficulty_history
            }
        
        return {
            'difficulty_history': [],
            'times_studied': 0,
            'last_studied': None,
            'mastery_level': 0
        }
    
    def get_set_progress(self, set_id: str) -> Dict:
        """Get overall progress for a study set"""
        if not self.user_id:
            return {
                'studied': 0,
                'mastered': 0,
                'learning': 0,
                'difficult': 0
            }
        
        return self.db.get_user_progress(self.user_id, set_id)
    
    def get_cards_by_difficulty(self, set_id: str) -> Dict[str, List[int]]:
        """Get card indices grouped by difficulty level"""
        if not self.user_id:
            return {'easy': [], 'learning': [], 'difficult': []}
        
        study_set = self.db.get_study_set(set_id, self.user_id)
        if not study_set:
            return {'easy': [], 'learning': [], 'difficult': []}
        
        easy_cards = []
        learning_cards = []
        difficult_cards = []
        
        for i, card in enumerate(study_set['cards']):
            progress = self.get_card_progress(set_id, i)
            mastery = progress['mastery_level']
            
            if mastery >= 8:
                easy_cards.append(i)
            elif mastery >= 3:
                learning_cards.append(i)
            else:
                difficult_cards.append(i)
        
        return {
            'easy': easy_cards,
            'learning': learning_cards,
            'difficult': difficult_cards
        }
    
    def get_study_streak(self, set_id: str) -> int:
        """Calculate study streak for a set (consecutive days studied)"""
        if not self.user_id:
            return 0
        
        study_dates = self.db.execute_query(
            """SELECT DISTINCT DATE(last_studied) as study_date 
               FROM study_progress 
               WHERE user_id = %s AND study_set_id = %s AND last_studied IS NOT NULL
               ORDER BY study_date DESC""",
            (self.user_id, set_id),
            fetch='all'
        )
        
        if not study_dates:
            return 0
        
        streak = 0
        today = datetime.now().date()
        
        for row in study_dates:
            study_date = row[0]
            if (today - study_date).days == streak:
                streak += 1
            else:
                break
        
        return streak
    
    def get_total_mastered(self) -> int:
        """Get total number of mastered cards across all sets"""
        if not self.user_id:
            return 0
        
        result = self.db.execute_query(
            """SELECT COUNT(*) FROM study_progress 
               WHERE user_id = %s AND mastery_level >= 8""",
            (self.user_id,),
            fetch='one'
        )
        
        return result[0] if result else 0
    
    def get_total_learning(self) -> int:
        """Get total number of cards being learned across all sets"""
        if not self.user_id:
            return 0
        
        result = self.db.execute_query(
            """SELECT COUNT(*) FROM study_progress 
               WHERE user_id = %s AND mastery_level >= 3 AND mastery_level < 8""",
            (self.user_id,),
            fetch='one'
        )
        
        return result[0] if result else 0
    
    def get_study_statistics(self) -> Dict:
        """Get comprehensive study statistics"""
        if not self.user_id:
            return {
                'total_cards_studied': 0,
                'total_study_sessions': 0,
                'total_mastered': 0,
                'total_learning': 0,
                'sets_with_progress': 0
            }
        
        stats = self.db.execute_query(
            """SELECT 
                COUNT(DISTINCT card_id) as cards_studied,
                SUM(times_studied) as total_sessions,
                SUM(CASE WHEN mastery_level >= 8 THEN 1 ELSE 0 END) as mastered,
                SUM(CASE WHEN mastery_level >= 3 AND mastery_level < 8 THEN 1 ELSE 0 END) as learning,
                COUNT(DISTINCT study_set_id) as sets_count
               FROM study_progress
               WHERE user_id = %s""",
            (self.user_id,),
            fetch='one'
        )
        
        if stats:
            return {
                'total_cards_studied': stats[0] or 0,
                'total_study_sessions': stats[1] or 0,
                'total_mastered': stats[2] or 0,
                'total_learning': stats[3] or 0,
                'sets_with_progress': stats[4] or 0
            }
        
        return {
            'total_cards_studied': 0,
            'total_study_sessions': 0,
            'total_mastered': 0,
            'total_learning': 0,
            'sets_with_progress': 0
        }
