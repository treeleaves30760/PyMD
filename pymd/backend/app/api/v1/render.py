"""Render API endpoints"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.redis import get_redis
from pymd.backend.app.core.security import get_current_user
from pymd.backend.app.models.user import User
from pymd.backend.app.schemas.render import (
    RenderRequest,
    RenderResponse,
    ValidationError,
    ValidationResponse,
)
from pymd.backend.app.services.render_service import RenderService

router = APIRouter(prefix="/render", tags=["render"])


@router.post(
    "",
    response_model=RenderResponse,
    summary="Render PyMD content",
)
async def render_content(
    request: RenderRequest,
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis),
):
    """
    Render PyMD content to HTML or Markdown.

    - **content**: PyMD content to render
    - **format**: Output format - "html" or "markdown" (default: "html")

    The result is cached in Redis for improved performance.
    """
    try:
        rendered, cached = await RenderService.render_pymd(
            content=request.content,
            format=request.format,
            redis=redis,
        )

        return RenderResponse(rendered=rendered, cached=cached)

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/preview",
    response_model=RenderResponse,
    summary="Quick preview rendering",
)
async def preview_render(
    request: RenderRequest,
    current_user: User = Depends(get_current_user),
    redis = Depends(get_redis),
):
    """
    Quick preview rendering with caching.

    This endpoint is optimized for live preview with debouncing.
    It uses Redis caching extensively to minimize rendering overhead.

    - **content**: PyMD content to render
    - **format**: Output format - "html" or "markdown" (default: "html")
    """
    try:
        rendered, cached = await RenderService.render_pymd(
            content=request.content,
            format=request.format,
            redis=redis,
        )

        return RenderResponse(rendered=rendered, cached=cached)

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


class ValidateRequest(BaseModel):
    """Request schema for validation"""
    content: str = Field(..., description="PyMD content to validate")


@router.post(
    "/validate",
    response_model=ValidationResponse,
    summary="Validate PyMD syntax",
)
async def validate_syntax(
    request: ValidateRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Validate PyMD syntax without rendering.

    Returns validation status and any errors found.

    - **content**: PyMD content to validate
    """
    try:
        is_valid, errors = await RenderService.validate_pymd_syntax(request.content)

        return ValidationResponse(
            valid=is_valid,
            errors=[ValidationError(**err) for err in errors],
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}",
        )


@router.get(
    "/documents/{document_id}",
    response_model=RenderResponse,
    summary="Render a stored document",
)
async def render_document(
    document_id: UUID,
    format: str = Query(
        "html",
        pattern="^(html|markdown)$",
        description="Output format",
    ),
    use_cache: bool = Query(
        True,
        description="Use cached render from database",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    Render a stored document.

    - **document_id**: UUID of the document to render
    - **format**: Output format - "html" or "markdown" (default: "html")
    - **use_cache**: Use cached render from database (default: true)

    The document must be owned by the current user.
    """
    try:
        rendered = await RenderService.render_document(
            db=db,
            redis=redis,
            document_id=document_id,
            user_id=current_user.id,
            format=format,
            use_cache=use_cache,
        )

        if rendered is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Cached is True if we used database cache
        return RenderResponse(rendered=rendered, cached=use_cache)

    except HTTPException:
        raise
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/documents/{document_id}/export",
    summary="Export document",
)
async def export_document(
    document_id: UUID,
    format: str = Query(
        "html",
        pattern="^(html|markdown|json)$",
        description="Export format",
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis = Depends(get_redis),
):
    """
    Export a document in various formats.

    - **document_id**: UUID of the document to export
    - **format**: Export format - "html", "markdown", or "json" (default: "html")

    Returns the file with appropriate Content-Type and Content-Disposition headers.
    """
    from pymd.backend.app.services.document_service import DocumentService

    # Get document
    document = await DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    # Handle different export formats
    if format == "json":
        # Export as JSON (original PyMD content + metadata)
        import json
        from datetime import datetime

        def json_serial(obj):
            """JSON serializer for objects not serializable by default"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            if hasattr(obj, "__str__"):
                return str(obj)
            raise TypeError(f"Type {type(obj)} not serializable")

        content = json.dumps(
            {
                "id": str(document.id),
                "title": document.title,
                "content": document.content,
                "render_format": document.render_format,
                "created_at": document.created_at.isoformat(),
                "updated_at": document.updated_at.isoformat(),
            },
            indent=2,
            default=json_serial,
        )
        media_type = "application/json"
        filename = f"{document.title}.json"

    else:
        # Render to HTML or Markdown
        try:
            rendered = await RenderService.render_document(
                db=db,
                redis=redis,
                document_id=document_id,
                user_id=current_user.id,
                format=format,
                use_cache=True,
            )

            if rendered is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found",
                )

            content = rendered
            media_type = "text/html" if format == "html" else "text/markdown"
            extension = "html" if format == "html" else "md"
            filename = f"{document.title}.{extension}"

        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export failed: {str(e)}",
            )

    # Return file with appropriate headers
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
