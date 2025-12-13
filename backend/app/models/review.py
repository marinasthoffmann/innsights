from typing import Optional
from sqlalchemy import String, Integer, Float, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from . import BaseModel


class ReviewStatus(enum.Enum):
    """
    Review processing status.
    
    Values:
        PENDING: Waiting for AI analysis
        PROCESSING: Currently being analyzed
        COMPLETED: Analysis finished successfully
        FAILED: Analysis failed
    """
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Review(BaseModel):
    """
    Review database model with AI analysis support.
    
    Attributes:
        id: Primary key
        hotel_id: Foreign key to hotels table
        user_name: Name of the reviewer
        rating: Star rating (1-5)
        title: Review title
        content: Full review text
        status: Processing status (pending/processing/completed/failed)
        
        AI Analysis Fields:
        sentiment_score: Overall sentiment (-1 to +1)
        sentiment_label: Sentiment classification (positive/negative/neutral)
        aspects: JSON with analyzed aspects (cleanliness, service, etc)
        topics: JSON with detected topics
        key_phrases: JSON with important phrases
        
        Relationships:
        hotel: Related hotel object
    """
    
    __tablename__ = "reviews"
    
    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    # Foreign Key
    hotel_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # User Information
    user_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )
    
    user_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )
    
    # Review Content
    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Star rating from 1 to 5"
    )
    
    title: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    
    # Processing Status
    status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus),
        default=ReviewStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # AI Analysis Results (populated by AI worker)
    sentiment_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Sentiment score from -1 (negative) to +1 (positive)"
    )
    
    sentiment_label: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        comment="Sentiment classification: positive, negative, neutral"
    )
    
    aspects: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Analyzed aspects with scores (e.g., cleanliness, service)"
    )
    
    topics: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="Detected topics in the review"
    )
    
    key_phrases: Mapped[Optional[list]] = mapped_column(
        JSON,
        nullable=True,
        comment="Important phrases extracted from review"
    )
    
    # # Relationships
    # hotel: Mapped["Hotel"] = relationship(
    #     "Hotel",
    #     back_populates="reviews"
    # )