"""User settings model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from pymd.backend.app.core.database import Base


class UserSettings(Base):
    """User settings model"""

    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    # UI preferences
    theme = Column(String(50), default="light", nullable=False)
    language = Column(String(10), default="en", nullable=False)

    # Editor settings (JSON)
    editor_settings = Column(
        JSONB,
        default={
            "fontSize": 14,
            "tabSize": 4,
            "wordWrap": True,
            "lineNumbers": True,
            "minimap": True,
        },
        nullable=False,
    )

    # Render settings (JSON)
    render_settings = Column(
        JSONB,
        default={
            "defaultFormat": "html",
            "autoRender": True,
            "syntaxHighlight": True,
        },
        nullable=False,
    )

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<UserSettings for user {self.user_id}>"
