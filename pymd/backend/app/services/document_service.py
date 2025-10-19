"""Document service for business logic"""
import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.models.document import Document
from pymd.backend.app.models.user import User
from pymd.backend.app.schemas.document import DocumentCreate, DocumentUpdate


class DocumentService:
    """Service for document operations"""

    @staticmethod
    def _compute_content_hash(content: str) -> str:
        """Compute SHA-256 hash of content"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    async def create_document(
        db: AsyncSession,
        user_id: UUID,
        document_data: DocumentCreate,
    ) -> Document:
        """Create a new document"""
        content_hash = DocumentService._compute_content_hash(document_data.content)

        document = Document(
            owner_id=user_id,
            title=document_data.title,
            content=document_data.content,
            content_hash=content_hash,
            render_format=document_data.render_format,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def get_document(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID,
    ) -> Optional[Document]:
        """Get a document by ID (only if user owns it)"""
        result = await db.execute(
            select(Document).where(
                and_(
                    Document.id == document_id,
                    Document.owner_id == user_id,
                    Document.is_deleted == False,
                )
            )
        )
        document = result.scalar_one_or_none()

        # Update last accessed time
        if document:
            document.last_accessed_at = datetime.utcnow()
            await db.commit()

        return document

    @staticmethod
    async def list_documents(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> tuple[list[Document], int]:
        """
        List documents for a user with pagination and search

        Returns:
            tuple: (documents, total_count)
        """
        # Build base query
        query = select(Document).where(
            and_(
                Document.owner_id == user_id,
                Document.is_deleted == False,
            )
        )

        # Add search filter if provided
        if search:
            search_filter = or_(
                Document.title.ilike(f"%{search}%"),
                Document.content.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Add sorting
        sort_column = getattr(Document, sort_by, Document.updated_at)
        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination
        query = query.offset(skip).limit(limit)

        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()

        return list(documents), total

    @staticmethod
    async def update_document(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID,
        document_data: DocumentUpdate,
    ) -> Optional[Document]:
        """Update a document"""
        # Get document (with ownership check)
        document = await DocumentService.get_document(db, document_id, user_id)
        if not document:
            return None

        # Update fields
        update_data = document_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(document, field, value)

        # Update content hash if content changed
        if "content" in update_data:
            document.content_hash = DocumentService._compute_content_hash(
                document.content
            )
            # Clear cached renders when content changes
            document.rendered_html = None
            document.rendered_markdown = None

        document.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def delete_document(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID,
    ) -> bool:
        """Soft delete a document"""
        document = await DocumentService.get_document(db, document_id, user_id)
        if not document:
            return False

        document.is_deleted = True
        document.updated_at = datetime.utcnow()

        await db.commit()

        return True

    @staticmethod
    async def duplicate_document(
        db: AsyncSession,
        document_id: UUID,
        user_id: UUID,
    ) -> Optional[Document]:
        """Duplicate a document"""
        # Get original document
        original = await DocumentService.get_document(db, document_id, user_id)
        if not original:
            return None

        # Create new document with copied content
        new_document = Document(
            owner_id=user_id,
            title=f"{original.title} (Copy)",
            content=original.content,
            content_hash=original.content_hash,
            render_format=original.render_format,
            # Don't copy cached renders
            rendered_html=None,
            rendered_markdown=None,
        )

        db.add(new_document)
        await db.commit()
        await db.refresh(new_document)

        return new_document

    @staticmethod
    async def search_documents(
        db: AsyncSession,
        user_id: UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Document], int]:
        """
        Full-text search documents using PostgreSQL tsvector
        Falls back to ILIKE if search_vector is not populated
        """
        # For now, use the list_documents with search parameter
        # In the future, we can enhance this to use search_vector for better performance
        return await DocumentService.list_documents(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            search=query,
        )

    @staticmethod
    async def get_document_count(
        db: AsyncSession,
        user_id: UUID,
    ) -> int:
        """Get total document count for a user"""
        result = await db.execute(
            select(func.count(Document.id)).where(
                and_(
                    Document.owner_id == user_id,
                    Document.is_deleted == False,
                )
            )
        )
        return result.scalar_one()

    @staticmethod
    async def update_cached_render(
        db: AsyncSession,
        document_id: UUID,
        format: str,
        rendered_content: str,
    ) -> bool:
        """Update cached render for a document"""
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            return False

        if format == "html":
            document.rendered_html = rendered_content
        elif format == "markdown":
            document.rendered_markdown = rendered_content

        await db.commit()

        return True
