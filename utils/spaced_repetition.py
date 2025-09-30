from datetime import datetime, timedelta
from typing import Tuple

class SpacedRepetition:
    """
    Spaced Repetition algorithm based on SM-2 (SuperMemo 2)
    
    The algorithm calculates optimal review intervals based on card difficulty
    and previous performance to maximize long-term retention.
    """
    
    @staticmethod
    def calculate_next_review(easiness_factor: float, repetitions: int, 
                              interval_days: int, quality: int) -> Tuple[float, int, int]:
        """
        Calculate next review parameters using SM-2 algorithm
        
        Args:
            easiness_factor: Current ease factor (>= 1.3)
            repetitions: Number of successful repetitions
            interval_days: Current interval in days
            quality: Quality of recall (0-5)
                0 = complete blackout
                1 = incorrect, but familiar
                2 = incorrect, but easy to recall correct answer
                3 = correct, but difficult
                4 = correct, with hesitation
                5 = perfect recall
        
        Returns:
            Tuple of (new_easiness_factor, new_repetitions, new_interval_days)
        """
        
        if quality < 3:
            repetitions = 0
            interval_days = 1
        else:
            easiness_factor = max(1.3, easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
            
            if repetitions == 0:
                interval_days = 1
            elif repetitions == 1:
                interval_days = 6
            else:
                interval_days = int(interval_days * easiness_factor)
            
            repetitions += 1
        
        return easiness_factor, repetitions, interval_days
    
    @staticmethod
    def map_difficulty_to_quality(difficulty: str) -> int:
        """
        Map user difficulty rating to SM-2 quality score
        
        Args:
            difficulty: 'hard', 'good', or 'easy'
        
        Returns:
            SM-2 quality score (0-5)
        """
        difficulty_map = {
            'hard': 2,
            'good': 4,
            'easy': 5
        }
        return difficulty_map.get(difficulty.lower(), 3)
    
    @staticmethod
    def get_next_review_date(easiness_factor: float, repetitions: int,
                            interval_days: int, difficulty: str) -> Tuple[datetime, float, int, int]:
        """
        Get the next review date and updated parameters
        
        Args:
            easiness_factor: Current ease factor
            repetitions: Current repetition count
            interval_days: Current interval
            difficulty: User's difficulty rating ('hard', 'good', 'easy')
        
        Returns:
            Tuple of (next_review_date, new_easiness, new_repetitions, new_interval)
        """
        quality = SpacedRepetition.map_difficulty_to_quality(difficulty)
        
        new_easiness, new_repetitions, new_interval = SpacedRepetition.calculate_next_review(
            easiness_factor, repetitions, interval_days, quality
        )
        
        next_review = datetime.now() + timedelta(days=new_interval)
        
        return next_review, new_easiness, new_repetitions, new_interval
    
    @staticmethod
    def is_due_for_review(next_review_date: datetime = None) -> bool:
        """
        Check if a card is due for review
        
        Args:
            next_review_date: The scheduled next review date
        
        Returns:
            True if the card should be reviewed now
        """
        if next_review_date is None:
            return True
        
        return datetime.now() >= next_review_date
    
    @staticmethod
    def get_cards_due_for_review(study_set_cards: list, progress_data: dict) -> list:
        """
        Filter cards that are due for review based on spaced repetition schedule
        
        Args:
            study_set_cards: List of all cards in the study set
            progress_data: Dictionary mapping card_index to progress info
        
        Returns:
            List of card indices that are due for review
        """
        due_cards = []
        
        for i, card in enumerate(study_set_cards):
            card_progress = progress_data.get(str(i), {})
            next_review = card_progress.get('next_review_date')
            
            if next_review is None or SpacedRepetition.is_due_for_review(next_review):
                due_cards.append(i)
        
        return due_cards
    
    @staticmethod
    def get_interval_category(interval_days: int) -> str:
        """
        Categorize the review interval for display purposes
        
        Args:
            interval_days: Interval in days
        
        Returns:
            Category string
        """
        if interval_days < 1:
            return "Learning"
        elif interval_days < 7:
            return "Young"
        elif interval_days < 30:
            return "Mature"
        else:
            return "Mastered"
