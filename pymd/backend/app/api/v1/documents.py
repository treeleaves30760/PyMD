"""Document API endpoints"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.security import get_current_user
from pymd.backend.app.models.user import User
from pymd.backend.app.schemas.document import (
    DocumentCreate,
    DocumentUpdate,
    DocumentResponse,
    DocumentListResponse,
)
from pymd.backend.app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


async def get_user_from_auth0_id(auth0_id: str, db: AsyncSession) -> User:
    """Helper to get User object from auth0_id"""
    result = await db.execute(select(User).where(User.auth0_id == auth0_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new document",
)
async def create_document(
    document_data: DocumentCreate,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new PyMD document.

    - **title**: Document title (required, 1-255 characters)
    - **content**: PyMD content (default: empty string)
    - **render_format**: Output format - "html" or "markdown" (default: "html")
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    document = await DocumentService.create_document(
        db=db,
        user_id=user.id,
        document_data=document_data,
    )

    return document


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List user's documents",
)
async def list_documents(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: str = Query(
        "updated_at",
        description="Sort field (created_at, updated_at, title)",
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all documents for the current user with pagination and search.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **search**: Optional search query (searches title and content)
    - **sort_by**: Field to sort by (default: "updated_at")
    - **sort_order**: "asc" or "desc" (default: "desc")
    """
    # Calculate skip
    skip = (page - 1) * page_size

    # Get documents and total count
    documents, total = await DocumentService.list_documents(
        db=db,
        user_id=(await get_user_from_auth0_id(auth0_id, db)).id,
        skip=skip,
        limit=page_size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    # Calculate has_more
    has_more = (skip + len(documents)) < total

    return DocumentListResponse(
        documents=documents,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get a document",
)
async def get_document(
    document_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a specific document by ID.

    Only the document owner can access it.
    """
    document = await DocumentService.get_document(
        db=db,
        document_id=document_id,
        user_id=(await get_user_from_auth0_id(auth0_id, db)).id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Update a document",
)
async def update_document(
    document_id: UUID,
    document_data: DocumentUpdate,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a document.

    Only the document owner can update it.

    - **title**: New title (optional)
    - **content**: New content (optional)
    - **render_format**: New render format (optional)
    """
    document = await DocumentService.update_document(
        db=db,
        document_id=document_id,
        user_id=(await get_user_from_auth0_id(auth0_id, db)).id,
        document_data=document_data,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a document",
)
async def delete_document(
    document_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Soft delete a document.

    Only the document owner can delete it.
    """
    success = await DocumentService.delete_document(
        db=db,
        document_id=document_id,
        user_id=(await get_user_from_auth0_id(auth0_id, db)).id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return None


@router.post(
    "/{document_id}/duplicate",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Duplicate a document",
)
async def duplicate_document(
    document_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a copy of an existing document.

    The new document will have " (Copy)" appended to the title.
    Only the document owner can duplicate it.
    """
    document = await DocumentService.duplicate_document(
        db=db,
        document_id=document_id,
        user_id=(await get_user_from_auth0_id(auth0_id, db)).id,
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document


@router.get(
    "/search",
    response_model=DocumentListResponse,
    summary="Search documents",
    deprecated=True,
)
async def search_documents(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Search documents (deprecated - use list_documents with search parameter).

    This endpoint is kept for backward compatibility.
    """
    skip = (page - 1) * page_size

    documents, total = await DocumentService.search_documents(
        db=db,
        user_id=(await get_user_from_auth0_id(auth0_id, db)).id,
        query=q,
        skip=skip,
        limit=page_size,
    )

    has_more = (skip + len(documents)) < total

    return DocumentListResponse(
        documents=documents,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )
