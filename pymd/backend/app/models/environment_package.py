"""Environment Package model"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, BigInteger, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from pymd.backend.app.core.database import Base


class EnvironmentPackage(Base):
    """Environment Package model - tracks installed packages in an environment"""

    __tablename__ = "environment_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_environments.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Package information
    package_name = Column(String(255), nullable=False)
    version = Column(String(100), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)

    # Timestamp
    installed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    environment = relationship("UserEnvironment", back_populates="packages")

    # Indexes and constraints
    __table_args__ = (
        Index("idx_pkg_env_id", "environment_id"),
        Index("idx_pkg_env_name", "environment_id", "package_name", unique=True),  # Unique package per env
    )

    def __repr__(self):
        return f"<EnvironmentPackage {self.package_name}=={self.version}>"
