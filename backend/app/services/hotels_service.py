import logging
from typing import Optional, Tuple, List
from repository.hotels_repository import HotelRepository
from models.hotel import Hotel

logger = logging.getLogger(__name__)

class HotelService:
    """
    Service class for hotel business logic.
    
    Orchestrates hotel operations and applies business rules.
    """

    def __init__(self, repository: Optional[HotelRepository] = None):
        """
        Initialize service with repository.
        
        Args:
            repository: HotelRepository instance (creates new if not provided)
        """
        self.repository = repository or HotelRepository()

    def list_hotels(
        self,
        page: int = 1,
        page_size: int = 20,
        city: Optional[str] = None,
        country: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> Tuple[List[Hotel], int, int]:
        """
        Get paginated list of hotels.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            city: Filter by city (optional)
            country: Filter by country (optional)
            min_rating: Minimum star rating (optional)
            
        Returns:
            Tuple of (hotels list, total count, total pages)
        """
        hotels, total = self.repository.get_all(
            page=page,
            page_size=page_size,
            city=city,
            country=country,
            min_rating=min_rating
        )
        
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return hotels, total, total_pages
    
    def get_hotel(self, hotel_id: int) -> Optional[Hotel]:
        """
        Get hotel by ID.
        
        Args:
            hotel_id: Hotel ID
            
        Returns:
            Hotel instance or None if not found
        """
        return self.repository.get_by_id(hotel_id)
    
    def create_hotel(self, hotel_data: dict) -> Hotel:
        """
        Create a new hotel.
        
        Args:
            hotel_data: Dictionary with hotel attributes
            
        Returns:
            Created Hotel instance
            
        Raises:
            ValueError: If hotel data is invalid
        """
        self._validate_hotel_data(hotel_data)
        
        hotel = self.repository.create(hotel_data)
        logger.info(f"Created hotel: {hotel.id} - {hotel.name}")
        
        return hotel
    
    def update_hotel(self, hotel_id: int, update_data: dict) -> Optional[Hotel]:
        """
        Update hotel information.
        
        Args:
            hotel_id: Hotel ID
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Hotel instance or None if not found
            
        Raises:
            ValueError: If update data is invalid
        """
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if update_data:
            self._validate_hotel_data(update_data, partial=True)
        
        hotel = self.repository.update(hotel_id, update_data)
        
        if hotel:
            logger.info(f"Updated hotel: {hotel_id}")
        
        return hotel
    
    def _validate_hotel_data(self, data: dict, partial: bool = False):
        """
        Validate hotel data according to business rules.
        
        Args:
            data: Hotel data to validate
            partial: If True, only validates present fields
            
        Raises:
            ValueError: If validation fails
        """
        if 'star_rating' in data:
            rating = data['star_rating']
            if rating is not None and not (1 <= rating <= 5):
                raise ValueError("Star rating must be between 1 and 5")
        
        if 'name' in data and not partial:
            if not data['name'] or not data['name'].strip():
                raise ValueError("Hotel name is required")
        
        if 'city' in data and not partial:
            if not data['city'] or not data['city'].strip():
                raise ValueError("City is required")
        
        if 'country' in data and not partial:
            if not data['country'] or not data['country'].strip():
                raise ValueError("Country is required")
            
    def delete_hotel(self, hotel_id: int) -> bool:
        """
        Delete a hotel.
        
        Args:
            hotel_id: Hotel ID
            
        Returns:
            True if deleted, False if not found
        """
        result = self.repository.delete(hotel_id)
        
        if result:
            logger.info(f"Deleted hotel: {hotel_id}")
        
        return result