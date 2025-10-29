"""Environment Execution model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import Enum as SQLEnum

from pymd.backend.app.core.database import Base


class ExecutionStatus(str, enum.Enum):
    """Execution status"""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class EnvironmentExecution(Base):
    """Environment Execution model - tracks code execution history"""

    __tablename__ = "environment_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_environments.id", ondelete="CASCADE"),
        nullable=False,
    )
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Execution status
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.QUEUED, nullable=False)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Execution metrics
    execution_time_ms = Column(Integer, nullable=True)  # Execution time in milliseconds

    # Error information
    error_message = Column(Text, nullable=True)

    # Relationships
    environment = relationship("UserEnvironment", back_populates="executions")
    document = relationship("Document")

    # Indexes
    __table_args__ = (
        Index("idx_exec_env_id", "environment_id"),
        Index("idx_exec_doc_id", "document_id"),
        Index("idx_exec_status", "status"),
        Index("idx_exec_created", "started_at"),
    )

    def __repr__(self):
        return f"<EnvironmentExecution {self.id} ({self.status})>"
