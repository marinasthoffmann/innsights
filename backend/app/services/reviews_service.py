import logging
from typing import Optional, Tuple, List
from repository.hotels_repository import HotelRepository
from repository.reviews_repository import ReviewRepository
from models.review import Review, ReviewStatus
from queue_publisher import get_publisher

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
        
        # Publish to RabbitMQ for analysis
        try:
            publisher = get_publisher()
            publisher.publish_review(
                review_id=review.id,
                review_data={
                    'content': review.content,
                    'title': review.title,
                    'rating': review.rating,
                    'hotel_id': review.hotel_id
                }
            )
            logger.info(f"✅ Review {review.id} sent to queue")
        except Exception as e:
            logger.error(f"⚠️ Error publishing review {review.id}: {e}")
        
        return review
    
    def list_reviews(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ReviewStatus] = None
    ) -> Tuple[List[Review], int, int]:
        """
        Get paginated list of all reviews.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Filter by status (optional)
            
        Returns:
            Tuple of (reviews list, total count, total pages)
        """
        reviews, total = self.review_repo.get_all(
            page=page,
            page_size=page_size,
            status=status
        )
        
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return reviews, total, total_pages    
    
    def list_hotel_reviews(
        self,
        hotel_id: int,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ReviewStatus] = None
    ) -> Tuple[List[Review], int, int]:
        """
        Get paginated reviews for a specific hotel.
        
        Args:
            hotel_id: Hotel ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            status: Filter by status (optional)
            
        Returns:
            Tuple of (reviews list, total count, total pages)
            
        Raises:
            ValueError: If hotel doesn't exist
        """
        if not self.hotel_repo.exists(hotel_id):
            raise ValueError(f"Hotel with ID {hotel_id} does not exist")
        
        reviews, total = self.review_repo.get_by_hotel(
            hotel_id=hotel_id,
            page=page,
            page_size=page_size,
            status=status
        )
        
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return reviews, total, total_pages
    
    def get_review(self, review_id: int, with_hotel: bool = False) -> Optional[Review]:
        """
        Get review by ID.
        
        Args:
            review_id: Review ID
            with_hotel: If True, include hotel data
            
        Returns:
            Review instance or None if not found
        """
        return self.review_repo.get_by_id(review_id, with_hotel=with_hotel)
    
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