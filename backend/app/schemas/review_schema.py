from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ReviewBase(BaseModel):
    """Base schema with common review fields"""
    
    hotel_id: int = Field(..., gt=0, description="ID of the hotel being reviewed")
    user_name: str = Field(..., min_length=1, max_length=100, description="Reviewer's name")
    rating: int = Field(..., ge=1, le=5, description="Star rating (1-5)")
    title: Optional[str] = Field(None, max_length=200, description="Review title")
    content: str = Field(..., min_length=10, description="Review text content")

class ReviewCreate(ReviewBase):
    """
    Schema for creating a new review.
    
    Example:
        {
            "hotel_id": 1,
            "user_name": "Marina Hoffmann",
            "rating": 5,
            "title": "Amazing stay!",
            "content": "The room was spotless and the staff were incredibly helpful..."
        }
    """
    pass

class AspectScore(BaseModel):
    """Schema for individual aspect analysis"""
    
    name: str = Field(..., description="Aspect name (e.g., cleanliness, service)")
    score: float = Field(..., ge=-1, le=1, description="Aspect sentiment score")
    sentiment: str = Field(..., description="Sentiment label (positive/negative/neutral)")

class ReviewAnalysis(BaseModel):
    """
    Schema for AI analysis results.
    
    Example:
        {
            "sentiment_score": 0.85,
            "sentiment_label": "positive",
            "aspects": [
                {"name": "cleanliness", "score": 0.9, "sentiment": "positive"},
                {"name": "service", "score": 0.8, "sentiment": "positive"}
            ],
            "topics": ["comfort", "breakfast", "location"],
            "key_phrases": ["room was spotless", "staff were helpful"]
        }
    """
    
    sentiment_score: float = Field(..., ge=-1, le=1, description="Overall sentiment score")
    sentiment_label: str = Field(..., description="Overall sentiment (positive/negative/neutral)")
    aspects: list[AspectScore] = Field(default_factory=list, description="Analyzed aspects")
    topics: list[str] = Field(default_factory=list, description="Detected topics")
    key_phrases: list[str] = Field(default_factory=list, description="Important phrases")

class ReviewResponse(ReviewBase):
    """
    Schema for review responses (includes database and analysis fields).
    
    Example:
        {
            "id": 1,
            "hotel_id": 1,
            "user_name": "Marina Hoffmann",
            "rating": 5,
            "status": "completed",
            "sentiment_score": 0.85,
            "sentiment_label": "positive",
            "aspects": [...],
            "created_at": "2025-12-12T08:30:00"
        }
    """
    
    id: int
    status: str = Field(..., description="Processing status")
    sentiment_score: Optional[float] = None
    sentiment_label: Optional[str] = None
    aspects: Optional[list[AspectScore]] = None
    topics: Optional[list[str]] = None
    key_phrases: Optional[list[str]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ReviewListResponse(BaseModel):
    """
    Schema for paginated review list responses.
    
    Example:
        {
            "items": [...],
            "total": 150,
            "page": 1,
            "page_size": 20,
            "total_pages": 8
        }
    """
    
    items: list[ReviewResponse]
    total: int = Field(..., description="Total number of reviews")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")