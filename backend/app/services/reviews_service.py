import logging
from typing import Optional
from repository.hotels_repository import HotelRepository
from repository.reviews_repository import ReviewRepository
from models.review import Review, ReviewStatus

logger = logging.getLogger(__name__)

class ReviewService:
    """
    Service class for review business logic.
    
    Handles review creation, retrieval, and AI processing coordination.
    """
    def __init__(
        self,
        review_repo: Optional[ReviewRepository] = None,
        hotel_repo: Optional[HotelRepository] = None
    ):
        """
        Initialize service with dependencies.
        
        Args:
            review_repo: ReviewRepository instance
            hotel_repo: HotelRepository instance
        """
        self.review_repo = review_repo or ReviewRepository()
        self.hotel_repo = hotel_repo or HotelRepository()

    def create_review(self, review_data: dict) -> Review:
        """
        Create a new review.
        
        Args:
            review_data: Dictionary with review attributes
            
        Returns:
            Created Review instance
            
        Raises:
            ValueError: If review data is invalid or hotel doesn't exist
        """
        hotel_id = review_data.get('hotel_id')
        if not self.hotel_repo.exists(hotel_id):
            raise ValueError(f"Hotel with ID {hotel_id} does not exist")
        
        self._validate_review_data(review_data)
        
        review_data['status'] = ReviewStatus.PENDING
        
        review = self.review_repo.create(review_data)
        logger.info(f"Created review: {review.id} for hotel: {hotel_id}")
        
        # TODO: Send to queue for AI analysis
        # if self.queue_service:
        #     self.queue_service.publish_review_for_analysis(review.id, review.content)
        
        return review
    
    def _validate_review_data(self, data: dict):
        """
        Validate review data according to business rules.
        
        Args:
            data: Review data to validate
            
        Raises:
            ValueError: If validation fails
        """
        rating = data.get('rating')
        if rating is not None:
            if not 1 <= rating <= 5:
                raise ValueError("Rating must be between 1 and 5")
        
        content = data.get('content', '').strip()
        if len(content) < 10:
            raise ValueError("Review content must be at least 10 characters")
        
        user_name = data.get('user_name', '').strip()
        if not user_name:
            raise ValueError("User name is required")