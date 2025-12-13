from datetime import datetime
from typing import Any, Dict
from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from extensions import db

Base = db.Model

class TimestampMixin:
    """
    Mixin that adds timestamp fields to models.
    
    Attributes:
        created_at: Record creation timestamp
        updated_at: Last update timestamp (auto-updated)
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class BaseModel(Base, TimestampMixin):
    """
    Abstract base model with common functionality.
    All models should inherit from this.
    """
    
    __abstract__ = True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.
        
        Returns:
            Dict with all column values
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """String representation of the model"""
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self.to_dict().items()
        )
        return f"{self.__class__.__name__}({attrs})"
    
from .review import Review, ReviewStatus 
from .hotel import Hotel

__all__ = ["Base", "BaseModel", "Hotel", "Review", "ReviewStatus", "db"]