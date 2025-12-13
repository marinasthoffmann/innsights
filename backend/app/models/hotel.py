from . import BaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, Float
from typing import Optional, List


class Hotel(BaseModel):
    """
    Hotel database model.
    
    Attributes:
        id: Primary key
        name: Hotel name
        city: City location
        country: Country location
        address: Full address
        description: Hotel description
        star_rating: Star rating (1-5)
        reviews: Related reviews (one-to-many)
    """
    
    __tablename__ = "hotels"
    
    # Primary Key
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    
    # Basic Information
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    # Ratings & Pricing
    star_rating: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True
    )
    
    # Relationships
    reviews = relationship(
        "Review",
        back_populates="hotel",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        return f"Hotel(id={self.id}, name='{self.name}', city='{self.city}')"
    
    @property
    def review_count(self) -> int:
        """Returns the total number of reviews for this hotel"""
        return len(self.reviews) if self.reviews else 0
    
    @property
    def location(self) -> str:
        """Returns formatted location string"""
        return f"{self.city}, {self.country}"