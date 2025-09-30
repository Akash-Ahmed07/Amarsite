import psycopg2
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

class Database:
    """Database connection and operations handler"""
    
    def __init__(self):
        self.connection_string = os.environ.get('DATABASE_URL')
        
    def get_connection(self):
        """Get a new database connection"""
        return psycopg2.connect(self.connection_string)
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = None):
        """Execute a query and optionally fetch results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(query, params)
            
            if fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'all':
                result = cursor.fetchall()
            else:
                result = None
            
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    
    def create_user(self, username: str, email: str, password_hash: str) -> Optional[int]:
        """Create a new user"""
        query = """
            INSERT INTO users (username, email, password_hash, created_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(
            query, 
            (username, email, password_hash, datetime.now()),
            fetch='one'
        )
        return result[0] if result else None
    
    def get_user_by_username(self, username: str) -> Optional[Tuple]:
        """Get user by username"""
        query = "SELECT id, username, email, password_hash FROM users WHERE username = %s"
        return self.execute_query(query, (username,), fetch='one')
    
    def get_user_by_email(self, email: str) -> Optional[Tuple]:
        """Get user by email"""
        query = "SELECT id, username, email, password_hash FROM users WHERE email = %s"
        return self.execute_query(query, (email,), fetch='one')
    
    def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        query = "UPDATE users SET last_login = %s WHERE id = %s"
        self.execute_query(query, (datetime.now(), user_id))
    
    def create_study_set(self, set_id: str, user_id: int, title: str, 
                         description: str, subject: str, is_public: bool = False) -> bool:
        """Create a new study set"""
        query = """
            INSERT INTO study_sets (id, user_id, title, description, subject, is_public, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        now = datetime.now()
        self.execute_query(query, (set_id, user_id, title, description, subject, is_public, now, now))
        return True
    
    def get_study_sets_by_user(self, user_id: int) -> List[Dict]:
        """Get all study sets for a user"""
        query = """
            SELECT s.id, s.title, s.description, s.subject, s.is_public, s.created_at,
                   COUNT(c.id) as card_count
            FROM study_sets s
            LEFT JOIN cards c ON s.id = c.study_set_id
            WHERE s.user_id = %s
            GROUP BY s.id
            ORDER BY s.created_at DESC
        """
        results = self.execute_query(query, (user_id,), fetch='all')
        
        study_sets = []
        for row in results or []:
            study_sets.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'subject': row[3],
                'is_public': row[4],
                'created_at': row[5].isoformat() if row[5] else None,
                'card_count': row[6] or 0
            })
        return study_sets
    
    def get_study_set(self, set_id: str, user_id: int = None) -> Optional[Dict]:
        """Get a specific study set with cards"""
        if user_id:
            query = """
                SELECT id, user_id, title, description, subject, is_public, created_at
                FROM study_sets
                WHERE id = %s AND (user_id = %s OR is_public = TRUE)
            """
            result = self.execute_query(query, (set_id, user_id), fetch='one')
        else:
            query = """
                SELECT id, user_id, title, description, subject, is_public, created_at
                FROM study_sets
                WHERE id = %s AND is_public = TRUE
            """
            result = self.execute_query(query, (set_id,), fetch='one')
        
        if not result:
            return None
        
        study_set = {
            'id': result[0],
            'user_id': result[1],
            'title': result[2],
            'description': result[3],
            'subject': result[4],
            'is_public': result[5],
            'created_at': result[6].isoformat() if result[6] else None,
            'cards': []
        }
        
        cards_query = """
            SELECT id, term, definition, term_image_url, definition_image_url, card_order
            FROM cards
            WHERE study_set_id = %s
            ORDER BY card_order
        """
        cards = self.execute_query(cards_query, (set_id,), fetch='all')
        
        for card in cards or []:
            study_set['cards'].append({
                'id': card[0],
                'term': card[1],
                'definition': card[2],
                'term_image_url': card[3],
                'definition_image_url': card[4],
                'card_order': card[5]
            })
        
        return study_set
    
    def add_card_to_set(self, study_set_id: str, term: str, definition: str, 
                        card_order: int, term_image_url: str = None, 
                        definition_image_url: str = None) -> int:
        """Add a card to a study set"""
        query = """
            INSERT INTO cards (study_set_id, term, definition, term_image_url, 
                             definition_image_url, card_order, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        result = self.execute_query(
            query, 
            (study_set_id, term, definition, term_image_url, definition_image_url, 
             card_order, datetime.now()),
            fetch='one'
        )
        return result[0] if result else None
    
    def update_card(self, card_id: int, term: str = None, definition: str = None,
                   term_image_url: str = None, definition_image_url: str = None) -> bool:
        """Update a card's content"""
        updates = []
        params = []
        
        if term is not None:
            updates.append("term = %s")
            params.append(term)
        if definition is not None:
            updates.append("definition = %s")
            params.append(definition)
        if term_image_url is not None:
            updates.append("term_image_url = %s")
            params.append(term_image_url)
        if definition_image_url is not None:
            updates.append("definition_image_url = %s")
            params.append(definition_image_url)
        
        if not updates:
            return False
        
        query = f"UPDATE cards SET {', '.join(updates)} WHERE id = %s"
        params.append(card_id)
        self.execute_query(query, tuple(params))
        return True
    
    def delete_card(self, card_id: int) -> bool:
        """Delete a single card"""
        query = "DELETE FROM cards WHERE id = %s"
        self.execute_query(query, (card_id,))
        return True
    
    def update_study_set(self, set_id: str, user_id: int, title: str = None,
                        description: str = None, subject: str = None, 
                        is_public: bool = None) -> bool:
        """Update study set metadata"""
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = %s")
            params.append(title)
        if description is not None:
            updates.append("description = %s")
            params.append(description)
        if subject is not None:
            updates.append("subject = %s")
            params.append(subject)
        if is_public is not None:
            updates.append("is_public = %s")
            params.append(is_public)
        
        if updates:
            updates.append("updated_at = %s")
            params.append(datetime.now())
            
            query = f"UPDATE study_sets SET {', '.join(updates)} WHERE id = %s AND user_id = %s"
            params.extend([set_id, user_id])
            self.execute_query(query, tuple(params))
        
        return True
    
    def delete_study_set(self, set_id: str, user_id: int) -> bool:
        """Delete a study set (cascade deletes cards and progress)"""
        query = "DELETE FROM study_sets WHERE id = %s AND user_id = %s"
        self.execute_query(query, (set_id, user_id))
        return True
    
    def update_study_progress(self, user_id: int, card_id: int, study_set_id: str,
                             difficulty: str, mastery_level: int) -> bool:
        """Update or create study progress for a card"""
        now = datetime.now()
        
        check_query = "SELECT id, difficulty_history, times_studied FROM study_progress WHERE user_id = %s AND card_id = %s"
        existing = self.execute_query(check_query, (user_id, card_id), fetch='one')
        
        if existing:
            difficulty_history_raw = existing[1]
            if isinstance(difficulty_history_raw, str):
                difficulty_history = json.loads(difficulty_history_raw)
            elif isinstance(difficulty_history_raw, list):
                difficulty_history = difficulty_history_raw
            else:
                difficulty_history = []
            
            difficulty_history.append({
                'difficulty': difficulty,
                'timestamp': now.isoformat()
            })
            
            times_studied = (existing[2] or 0) + 1
            
            update_query = """
                UPDATE study_progress 
                SET mastery_level = %s, times_studied = %s, last_studied = %s, 
                    difficulty_history = %s, next_review_date = %s
                WHERE user_id = %s AND card_id = %s
            """
            next_review = self.calculate_next_review(mastery_level, now)
            self.execute_query(
                update_query,
                (mastery_level, times_studied, now, json.dumps(difficulty_history), 
                 next_review, user_id, card_id)
            )
        else:
            difficulty_history = [{
                'difficulty': difficulty,
                'timestamp': now.isoformat()
            }]
            
            insert_query = """
                INSERT INTO study_progress (user_id, card_id, study_set_id, mastery_level, 
                                           times_studied, last_studied, difficulty_history, next_review_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            next_review = self.calculate_next_review(mastery_level, now)
            self.execute_query(
                insert_query,
                (user_id, card_id, study_set_id, mastery_level, 1, now, 
                 json.dumps(difficulty_history), next_review)
            )
        
        return True
    
    def calculate_next_review(self, mastery_level: int, current_time: datetime) -> datetime:
        """Calculate next review date based on mastery level (basic spaced repetition)"""
        from datetime import timedelta
        
        intervals = {
            0: timedelta(hours=1),
            1: timedelta(hours=4),
            2: timedelta(hours=12),
            3: timedelta(days=1),
            4: timedelta(days=2),
            5: timedelta(days=4),
            6: timedelta(days=7),
            7: timedelta(days=14),
            8: timedelta(days=30),
            9: timedelta(days=60),
            10: timedelta(days=120)
        }
        
        interval = intervals.get(mastery_level, timedelta(days=1))
        return current_time + interval
    
    def get_user_progress(self, user_id: int, study_set_id: str) -> Dict:
        """Get progress statistics for a user on a specific study set"""
        query = """
            SELECT 
                COUNT(*) as studied,
                SUM(CASE WHEN mastery_level >= 8 THEN 1 ELSE 0 END) as mastered,
                SUM(CASE WHEN mastery_level >= 3 AND mastery_level < 8 THEN 1 ELSE 0 END) as learning,
                SUM(CASE WHEN mastery_level < 3 THEN 1 ELSE 0 END) as difficult
            FROM study_progress
            WHERE user_id = %s AND study_set_id = %s
        """
        result = self.execute_query(query, (user_id, study_set_id), fetch='one')
        
        if result:
            return {
                'studied': result[0] or 0,
                'mastered': result[1] or 0,
                'learning': result[2] or 0,
                'difficult': result[3] or 0
            }
        return {'studied': 0, 'mastered': 0, 'learning': 0, 'difficult': 0}
    
    def get_public_study_sets(self, limit: int = 50) -> List[Dict]:
        """Get public study sets for the library"""
        query = """
            SELECT s.id, s.title, s.description, s.subject, s.created_at,
                   u.username, COUNT(c.id) as card_count
            FROM study_sets s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN cards c ON s.id = c.study_set_id
            WHERE s.is_public = TRUE
            GROUP BY s.id, u.username
            ORDER BY s.created_at DESC
            LIMIT %s
        """
        results = self.execute_query(query, (limit,), fetch='all')
        
        study_sets = []
        for row in results or []:
            study_sets.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'subject': row[3],
                'created_at': row[4].isoformat() if row[4] else None,
                'author': row[5],
                'card_count': row[6] or 0
            })
        return study_sets
    
    def create_share_link(self, study_set_id: str, share_code: str) -> bool:
        """Create a share link for a study set"""
        query = """
            INSERT INTO study_set_shares (study_set_id, share_code, created_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (share_code) DO NOTHING
        """
        self.execute_query(query, (study_set_id, share_code, datetime.now()))
        return True
    
    def get_study_set_by_share_code(self, share_code: str) -> Optional[str]:
        """Get study set ID by share code"""
        query = "SELECT study_set_id FROM study_set_shares WHERE share_code = %s"
        result = self.execute_query(query, (share_code,), fetch='one')
        return result[0] if result else None
