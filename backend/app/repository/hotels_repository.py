from extensions import db
from typing import Optional, Tuple, List
from models.hotel import Hotel
from sqlalchemy import select, func

class HotelRepository:
    """
    Repository for Hotel database operations.
    
    Provides CRUD operations and queries for Hotel entities.
    All methods work within the current database session.
    """

    def __init__(self, session=None):
        """
        Initialize repository with database session.
        
        Args:
            session: SQLAlchemy session (uses db.session if not provided)
        """
        self.session = session or db.session

    def get_all(
        self, 
        page: int = 1, 
        page_size: int = 20,
        city: Optional[str] = None,
        country: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> Tuple[List[Hotel], int]:
        """
        Get paginated list of hotels with optional filters.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            city: Filter by city (case-insensitive, partial match)
            country: Filter by country (case-insensitive, partial match)
            min_rating: Minimum star rating filter
            
        Returns:
            Tuple of (list of hotels, total count)
        """
        query = select(Hotel)
        
        # Apply filters
        if city:
            query = query.where(Hotel.city.ilike(f'%{city}%'))
        if country:
            query = query.where(Hotel.country.ilike(f'%{country}%'))
        if min_rating is not None:
            query = query.where(Hotel.star_rating >= min_rating)
        
        # Get total count
        total = self.session.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        # Apply pagination and ordering
        query = query.order_by(Hotel.name).offset((page - 1) * page_size).limit(page_size)
        
        # Execute query
        hotels = list(self.session.scalars(query).all())
        
        return hotels, total
    
    def get_by_id(self, hotel_id: int) -> Optional[Hotel]:
        """
        Get hotel by ID.
        
        Args:
            hotel_id: Hotel ID
            
        Returns:
            Hotel instance or None if not found
        """
        return self.session.get(Hotel, hotel_id)
    
    def create(self, hotel_data: dict) -> Hotel:
        """
        Create a new hotel.
        
        Args:
            hotel_data: Dictionary with hotel attributes
            
        Returns:
            Created Hotel instance
        """
        hotel = Hotel(**hotel_data)
        self.session.add(hotel)
        self.session.commit()
        self.session.refresh(hotel)
        return hotel
    
    def update(self, hotel_id: int, update_data: dict) -> Optional[Hotel]:
        """
        Update hotel by ID.
        
        Args:
            hotel_id: Hotel ID
            update_data: Dictionary with fields to update
            
        Returns:
            Updated Hotel instance or None if not found
        """
        hotel = self.get_by_id(hotel_id)
        if not hotel:
            return None
        
        for key, value in update_data.items():
            if value is not None and hasattr(hotel, key):
                setattr(hotel, key, value)
        
        self.session.commit()
        self.session.refresh(hotel)
        return hotel
    
    def delete(self, hotel_id: int) -> bool:
        """
        Delete hotel by ID.
        
        Args:
            hotel_id: Hotel ID
            
        Returns:
            True if deleted, False if not found
        """
        hotel = self.get_by_id(hotel_id)
        if not hotel:
            return False
        
        self.session.delete(hotel)
        self.session.commit()
        return True
    
    def exists(self, hotel_id: int) -> bool:
        """
        Check if hotel exists.
        
        Args:
            hotel_id: Hotel ID
            
        Returns:
            True if exists, False otherwise
        """
        return self.session.scalar(
            select(func.count()).where(Hotel.id == hotel_id)
        ) > 0