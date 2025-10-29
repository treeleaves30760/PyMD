"""User Environment model"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, BigInteger, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import Enum as SQLEnum

from pymd.backend.app.core.database import Base


class EnvironmentStatus(str, enum.Enum):
    """Environment status"""

    ACTIVE = "active"
    CREATING = "creating"
    ERROR = "error"
    DELETED = "deleted"


class UserEnvironment(Base):
    """User Environment model - represents a Python environment for a user"""

    __tablename__ = "user_environments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    # Environment identification
    # e.g., "default", "data-science"
    name = Column(String(100), nullable=False)
    python_version = Column(String(20), default="3.11", nullable=False)

    # Docker volume name for persistence
    volume_name = Column(String(255), unique=True, nullable=False, index=True)

    # Status tracking
    status = Column(SQLEnum(EnvironmentStatus),
                    default=EnvironmentStatus.ACTIVE, nullable=False)

    # Resource tracking
    total_size_bytes = Column(BigInteger, default=0, nullable=False)
    package_count = Column(Integer, default=0, nullable=False)

    # Timestamps
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(
        timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(
        timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user = relationship("User", back_populates="environments")
    packages = relationship(
        "EnvironmentPackage", back_populates="environment", cascade="all, delete-orphan"
    )
    executions = relationship(
        "EnvironmentExecution", back_populates="environment", cascade="all, delete-orphan"
    )

    # Indexes and constraints
    __table_args__ = (
        Index("idx_env_user_id", "user_id"),
        Index("idx_env_last_used", "last_used_at"),
        Index("idx_env_user_name", "user_id", "name",
              unique=True),  # Unique name per user
    )

    def __repr__(self):
        return f"<UserEnvironment {self.name} ({self.user_id})>"
