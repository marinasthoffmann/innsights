from extensions import db
from models.review import Review

class ReviewRepository:
    """
    Repository for Review database operations.
    
    Provides CRUD operations and specialized queries for Review entities.
    """

    def __init__(self, session=None):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session (uses db.session if not provided)
        """
        self.session = session or db.session

    def create(self, review_data: dict) -> Review:
        """
        Create a new review.
        
        Args:
            review_data: Dictionary with review attributes
            
        Returns:
            Created Review instance
        """
        review = Review(**review_data)
        self.session.add(review)
        self.session.commit()
        self.session.refresh(review)
        return review