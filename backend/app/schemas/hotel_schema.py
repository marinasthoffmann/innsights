from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class HotelBase(BaseModel):
    """Base schema with common hotel fields"""
    
    name: str = Field(..., min_length=1, max_length=200, description="Hotel name")
    city: str = Field(..., min_length=1, max_length=100, description="City location")
    country: str = Field(..., min_length=1, max_length=100, description="Country location")
    address: Optional[str] = Field(None, max_length=500, description="Full address")
    description: Optional[str] = Field(None, description="Hotel description")
    star_rating: Optional[float] = Field(None, ge=1, le=5, description="Star rating (1-5)")

class HotelCreate(HotelBase):
    """
    Schema for creating a new hotel.
    
    Example:
        {
            "name": "Grand Plaza Hotel",
            "city": "New York",
            "country": "USA",
            "address": "123 Main St, NY 10001",
            "description": "Luxury hotel in the heart of Manhattan",
            "star_rating": 4.5
        }
    """
    pass

class HotelUpdate(BaseModel):
    """
    Schema for updating a hotel (all fields optional).
    
    Example:
        {
            "description": "Updated description"
        }
    """
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    address: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    star_rating: Optional[float] = Field(None, ge=1, le=5)

class HotelResponse(HotelBase):
    """
    Schema for hotel responses (includes database fields).
    
    Example:
        {
            "id": 1,
            "name": "Grand Plaza Hotel",
            "city": "New York",
            "country": "USA",
            "review_count": 45,
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-20T14:22:00"
        }
    """
    
    id: int
    review_count: int = Field(default=0, description="Total number of reviews")
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True, exclude=['reviews'])

class HotelListResponse(BaseModel):
    """
    Schema for paginated hotel list responses.
    
    Example:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
    """
    
    items: list[HotelResponse]
    total: int = Field(..., description="Total number of hotels")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")