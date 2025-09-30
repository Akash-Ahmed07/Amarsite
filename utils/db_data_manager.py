from typing import Dict, List, Optional
from utils.db import Database
import uuid

class DBDataManager:
    """Database-backed data manager for study sets and cards"""
    
    def __init__(self, user_id: int = None):
        self.db = Database()
        self.user_id = user_id
    
    def set_user(self, user_id: int):
        """Set the current user ID"""
        self.user_id = user_id
    
    def save_study_set(self, set_id: str, study_set: Dict) -> bool:
        """Save a study set to database"""
        if not self.user_id:
            return False
        
        self.db.create_study_set(
            set_id=set_id,
            user_id=self.user_id,
            title=study_set['title'],
            description=study_set.get('description', ''),
            subject=study_set.get('subject', 'Other'),
            is_public=study_set.get('privacy', 'Private') == 'Public'
        )
        
        for i, card in enumerate(study_set.get('cards', [])):
            self.db.add_card_to_set(
                study_set_id=set_id,
                term=card['term'],
                definition=card['definition'],
                card_order=i,
                term_image_url=card.get('term_image_url'),
                definition_image_url=card.get('definition_image_url')
            )
        
        return True
    
    def get_study_set(self, set_id: str) -> Optional[Dict]:
        """Get a specific study set"""
        study_set = self.db.get_study_set(set_id, self.user_id)
        
        if not study_set:
            return None
        
        formatted_cards = []
        for card in study_set.get('cards', []):
            formatted_cards.append({
                'term': card['term'],
                'definition': card['definition'],
                'term_image_url': card.get('term_image_url'),
                'definition_image_url': card.get('definition_image_url')
            })
        
        return {
            'id': study_set['id'],
            'title': study_set['title'],
            'description': study_set['description'],
            'subject': study_set['subject'],
            'privacy': 'Public' if study_set['is_public'] else 'Private',
            'cards': formatted_cards,
            'created_date': study_set['created_at'],
            'card_count': len(formatted_cards)
        }
    
    def get_all_sets(self) -> Dict:
        """Get all study sets for current user"""
        if not self.user_id:
            return {}
        
        sets = self.db.get_study_sets_by_user(self.user_id)
        
        result = {}
        for study_set in sets:
            full_set = self.get_study_set(study_set['id'])
            if full_set:
                result[study_set['id']] = full_set
        
        return result
    
    def delete_study_set(self, set_id: str) -> bool:
        """Delete a study set"""
        if not self.user_id:
            return False
        
        return self.db.delete_study_set(set_id, self.user_id)
    
    def update_study_set(self, set_id: str, updates: Dict) -> bool:
        """Update a study set"""
        if not self.user_id:
            return False
        
        return self.db.update_study_set(
            set_id=set_id,
            user_id=self.user_id,
            title=updates.get('title'),
            description=updates.get('description'),
            subject=updates.get('subject'),
            is_public=updates.get('privacy') == 'Public' if 'privacy' in updates else None
        )
    
    def search_study_sets(self, query: str) -> Dict:
        """Search study sets (basic implementation)"""
        all_sets = self.get_all_sets()
        query = query.lower()
        results = {}
        
        for set_id, study_set in all_sets.items():
            title_match = query in study_set.get('title', '').lower()
            desc_match = query in study_set.get('description', '').lower()
            
            if title_match or desc_match:
                results[set_id] = study_set
        
        return results
    
    def get_sets_by_subject(self, subject: str) -> Dict:
        """Get all study sets for a specific subject"""
        all_sets = self.get_all_sets()
        results = {}
        
        for set_id, study_set in all_sets.items():
            if study_set.get('subject', '').lower() == subject.lower():
                results[set_id] = study_set
        
        return results
    
    def get_study_stats(self) -> Dict:
        """Get overall statistics about study sets"""
        if not self.user_id:
            return {
                'total_sets': 0,
                'total_cards': 0,
                'subjects': {},
                'avg_cards_per_set': 0
            }
        
        all_sets = self.get_all_sets()
        total_sets = len(all_sets)
        total_cards = sum(len(study_set.get('cards', [])) for study_set in all_sets.values())
        
        subjects = {}
        for study_set in all_sets.values():
            subject = study_set.get('subject', 'Other')
            subjects[subject] = subjects.get(subject, 0) + 1
        
        return {
            'total_sets': total_sets,
            'total_cards': total_cards,
            'subjects': subjects,
            'avg_cards_per_set': total_cards / total_sets if total_sets > 0 else 0
        }
