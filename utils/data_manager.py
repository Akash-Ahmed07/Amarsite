import json
import os
from typing import Dict, List, Optional

class DataManager:
    """Manages study sets data persistence using JSON files"""
    
    def __init__(self, data_file: str = "study_sets.json"):
        self.data_file = data_file
        self.study_sets = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load study sets from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_data(self) -> bool:
        """Save study sets to JSON file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.study_sets, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def save_study_set(self, set_id: str, study_set: Dict) -> bool:
        """Save a study set"""
        self.study_sets[set_id] = study_set
        return self._save_data()
    
    def get_study_set(self, set_id: str) -> Optional[Dict]:
        """Get a specific study set by ID"""
        return self.study_sets.get(set_id)
    
    def get_all_sets(self) -> Dict:
        """Get all study sets"""
        return self.study_sets.copy()
    
    def delete_study_set(self, set_id: str) -> bool:
        """Delete a study set"""
        if set_id in self.study_sets:
            del self.study_sets[set_id]
            return self._save_data()
        return False
    
    def update_study_set(self, set_id: str, updates: Dict) -> bool:
        """Update a study set with new data"""
        if set_id in self.study_sets:
            self.study_sets[set_id].update(updates)
            return self._save_data()
        return False
    
    def search_study_sets(self, query: str) -> Dict:
        """Search study sets by title or description"""
        query = query.lower()
        results = {}
        
        for set_id, study_set in self.study_sets.items():
            title_match = query in study_set.get('title', '').lower()
            desc_match = query in study_set.get('description', '').lower()
            
            if title_match or desc_match:
                results[set_id] = study_set
        
        return results
    
    def get_sets_by_subject(self, subject: str) -> Dict:
        """Get all study sets for a specific subject"""
        results = {}
        
        for set_id, study_set in self.study_sets.items():
            if study_set.get('subject', '').lower() == subject.lower():
                results[set_id] = study_set
        
        return results
    
    def get_study_stats(self) -> Dict:
        """Get overall statistics about study sets"""
        total_sets = len(self.study_sets)
        total_cards = sum(len(study_set.get('cards', [])) for study_set in self.study_sets.values())
        
        subjects = {}
        for study_set in self.study_sets.values():
            subject = study_set.get('subject', 'Other')
            subjects[subject] = subjects.get(subject, 0) + 1
        
        return {
            'total_sets': total_sets,
            'total_cards': total_cards,
            'subjects': subjects,
            'avg_cards_per_set': total_cards / total_sets if total_sets > 0 else 0
        }
