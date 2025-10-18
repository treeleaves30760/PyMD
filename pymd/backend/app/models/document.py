"""Document model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship

from pymd.backend.app.core.database import Base


class Document(Base):
    """Document model"""

    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False, default="")
    content_hash = Column(String(64), nullable=True, index=True)

    # Render settings
    render_format = Column(String(50), default="html", nullable=False)

    # Cached renders
    rendered_html = Column(Text, nullable=True)
    rendered_markdown = Column(Text, nullable=True)

    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Full-text search
    search_vector = Column(TSVECTOR, nullable=True)

    # Relationships
    owner = relationship("User", back_populates="documents")

    # Indexes
    __table_args__ = (
        Index("idx_owner_created", "owner_id", "created_at"),
        Index("idx_owner_updated", "owner_id", "updated_at"),
        Index("idx_search_vector", "search_vector", postgresql_using="gin"),
    )

    def __repr__(self):
        return f"<Document {self.title}>"
