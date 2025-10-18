"""Document schemas"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """Base document schema"""

    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(default="")
    render_format: str = Field(default="html", pattern="^(html|markdown)$")


class DocumentCreate(DocumentBase):
    """Document creation schema"""

    pass


class DocumentUpdate(BaseModel):
    """Document update schema"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    render_format: Optional[str] = Field(None, pattern="^(html|markdown)$")


class DocumentResponse(DocumentBase):
    """Document response schema"""

    id: UUID
    owner_id: UUID
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Document list response with pagination"""

    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    has_more: bool
