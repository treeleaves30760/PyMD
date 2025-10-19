"""Render schemas"""
from pydantic import BaseModel, Field


class RenderRequest(BaseModel):
    """Request schema for rendering PyMD content"""

    content: str = Field(..., description="PyMD content to render")
    format: str = Field(
        "html",
        pattern="^(html|markdown)$",
        description="Output format",
    )


class RenderResponse(BaseModel):
    """Response schema for rendered content"""

    rendered: str = Field(..., description="Rendered content")
    cached: bool = Field(..., description="Whether result was from cache")


class ValidationError(BaseModel):
    """Validation error details"""

    line: int
    column: int
    message: str
    severity: str = Field(pattern="^(error|warning)$")


class ValidationResponse(BaseModel):
    """Response schema for validation"""

    valid: bool
    errors: list[ValidationError] = Field(default_factory=list)
