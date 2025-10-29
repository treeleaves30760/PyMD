"""Environment schemas"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class EnvironmentBase(BaseModel):
    """Base environment schema"""

    name: str = Field(..., min_length=1, max_length=100, description="Environment name")
    python_version: str = Field(default="3.11", pattern="^3\\.1[0-9]$", description="Python version")


class EnvironmentCreate(EnvironmentBase):
    """Environment creation schema"""

    pass


class EnvironmentUpdate(BaseModel):
    """Environment update schema"""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    python_version: Optional[str] = Field(None, pattern="^3\\.1[0-9]$")


class EnvironmentResponse(BaseModel):
    """Environment response schema"""

    id: UUID
    user_id: UUID
    name: str
    python_version: str
    volume_name: str
    status: str
    total_size_bytes: int
    package_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EnvironmentListResponse(BaseModel):
    """Environment list response"""

    environments: List[EnvironmentResponse]
    total: int


class EnvironmentStatsResponse(BaseModel):
    """Environment statistics response"""

    environment_count: int
    environment_limit: int
    total_size_bytes: int
    size_limit_bytes: int
    total_packages: int
    package_limit: int
    can_create_environment: bool


class PackageBase(BaseModel):
    """Base package schema"""

    package_name: str = Field(..., min_length=1, max_length=255, description="Package name")
    version: Optional[str] = Field(None, max_length=100, description="Package version")


class PackageInstallRequest(BaseModel):
    """Package installation request"""

    packages: List[str] = Field(..., min_items=1, max_items=10, description="List of packages to install")


class PackageResponse(BaseModel):
    """Package response schema"""

    id: UUID
    environment_id: UUID
    package_name: str
    version: Optional[str]
    size_bytes: Optional[int]
    installed_at: datetime

    model_config = {"from_attributes": True}


class PackageListResponse(BaseModel):
    """Package list response"""

    packages: List[PackageResponse]
    total: int
    total_size_bytes: int


class ExecutionRequest(BaseModel):
    """Code execution request"""

    code: str = Field(..., min_length=1, description="Python code to execute")
    environment_id: Optional[UUID] = Field(None, description="Environment ID (uses default if not provided)")


class ExecutionResponse(BaseModel):
    """Code execution response"""

    success: bool
    stdout: str
    stderr: str
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    environment_id: UUID
