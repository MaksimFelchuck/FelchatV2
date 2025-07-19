"""SQLAlchemy models for users and user blocks."""

import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from src.db.base import Base


class User(Base):
    """User model representing application users."""
    
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, 
        default=datetime.datetime.utcnow, 
        onupdate=datetime.datetime.utcnow
    )

    def __repr__(self):
        """String representation of the user."""
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class UserBlock(Base):
    """User block model representing blocked relationships between users."""
    
    __tablename__ = "user_blocks"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Ensure unique blocking relationship
    __table_args__ = (
        UniqueConstraint('blocker_id', 'blocked_id', name='unique_block'),
    )

    def __repr__(self):
        """String representation of the user block."""
        return (
            f"<UserBlock(blocker_id={self.blocker_id}, "
            f"blocked_id={self.blocked_id})>"
        )
