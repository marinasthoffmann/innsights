from extensions import db
from models.review import Review
from typing import Optional, Tuple, List
from models.review import ReviewStatus
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload


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
    
    def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ReviewStatus] = None
    ) -> Tuple[List[Review], int]:
        """
        Get all reviews with pagination and optional status filter.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Filter by review status (optional)
            
        Returns:
            Tuple of (list of reviews, total count)
        """
        query = select(Review)
        
        if status:
            query = query.where(Review.status == status)
        
        query = query.order_by(Review.created_at.desc())
        
        total = self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        query = query.offset((page - 1) * page_size).limit(page_size)
        reviews = list(self.session.scalars(query).all())
        
        return reviews, total
    
    def get_by_hotel(
        self,
        hotel_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ReviewStatus] = None
    ) -> Tuple[List[Review], int]:
        """
        Get paginated reviews for a specific hotel.
        
        Args:
            hotel_id: Hotel ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Filter by review status (optional)
            
        Returns:
            Tuple of (list of reviews, total count)
        """
        query = select(Review).where(Review.hotel_id == hotel_id)
    
        if status:
            query = query.where(Review.status == status)
  
        query = query.order_by(Review.created_at.desc())

        total = self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
 
        query = query.offset((page - 1) * page_size).limit(page_size)

        reviews = list(self.session.scalars(query).all())
        
        return reviews, total
    
    def get_by_id(self, review_id: int, with_hotel: bool = False) -> Optional[Review]:
        """
        Get review by ID.
        
        Args:
            review_id: Review ID
            with_hotel: If True, eagerly load hotel relationship
            
        Returns:
            Review instance or None if not found
        """
        query = select(Review).where(Review.id == review_id)
        
        if with_hotel:
            query = query.options(joinedload(Review.hotel))
        
        return self.session.scalar(query)