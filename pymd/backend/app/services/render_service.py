"""Render service for PyMD rendering"""
import hashlib
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.services.document_service import DocumentService


class RenderService:
    """Service for rendering PyMD content"""

    CACHE_TTL = 3600  # 1 hour cache TTL
    CACHE_PREFIX = "render:"

    @staticmethod
    def _compute_cache_key(content: str, format: str) -> str:
        """Compute cache key for rendered content"""
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"{RenderService.CACHE_PREFIX}{format}:{content_hash}"

    @staticmethod
    async def render_pymd(
        content: str,
        format: str = "html",
        redis: Optional[Redis] = None,
    ) -> Tuple[str, bool]:
        """
        Render PyMD content to HTML or Markdown

        Args:
            content: PyMD content to render
            format: Output format ("html" or "markdown")
            redis: Optional Redis client for caching

        Returns:
            Tuple of (rendered_content, cached)
            - rendered_content: The rendered output
            - cached: Whether result was from cache
        """
        # Check cache first
        if redis:
            cache_key = RenderService._compute_cache_key(content, format)
            cached_result = await redis.get(cache_key)
            if cached_result:
                # Handle both bytes and string responses from Redis
                if isinstance(cached_result, bytes):
                    return cached_result.decode("utf-8"), True
                return cached_result, True

        # Render using PyMD CLI
        try:
            rendered = await RenderService._render_with_cli(content, format)
        except Exception as e:
            raise RuntimeError(f"Failed to render PyMD content: {str(e)}")

        # Cache the result
        if redis:
            cache_key = RenderService._compute_cache_key(content, format)
            await redis.setex(cache_key, RenderService.CACHE_TTL, rendered)

        return rendered, False

    @staticmethod
    async def _render_with_cli(content: str, format: str) -> str:
        """
        Render PyMD content using the PyMD CLI

        This method creates a temporary file, runs the PyMD CLI, and returns the output
        """
        # Create temporary files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".pymd", delete=False
        ) as input_file:
            input_file.write(content)
            input_path = input_file.name

        try:
            output_suffix = ".html" if format == "html" else ".md"
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=output_suffix, delete=False
            ) as output_file:
                output_path = output_file.name

            # Run PyMD CLI
            # Note: The command assumes PyMD is installed and available
            cmd = [
                "python",
                "-m",
                "pymd.cli",
                "render",
                input_path,
                "-f",
                format,
                "-o",
                output_path,
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # 30 second timeout
                check=True,
            )

            # Read the output
            with open(output_path, "r", encoding="utf-8") as f:
                rendered = f.read()

            return rendered

        except subprocess.TimeoutExpired:
            raise RuntimeError("PyMD rendering timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"PyMD rendering failed: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error during rendering: {str(e)}")
        finally:
            # Clean up temporary files
            Path(input_path).unlink(missing_ok=True)
            if "output_path" in locals():
                Path(output_path).unlink(missing_ok=True)

    @staticmethod
    async def validate_pymd_syntax(content: str) -> Tuple[bool, list[dict]]:
        """
        Validate PyMD syntax without rendering

        Returns:
            Tuple of (is_valid, errors)
            - is_valid: Whether the syntax is valid
            - errors: List of error dictionaries with line, column, message, severity
        """
        # For now, we'll attempt to render and catch errors
        # In the future, we can implement a proper validator
        try:
            await RenderService._render_with_cli(content, "html")
            return True, []
        except RuntimeError as e:
            # Parse error message to extract line/column info if available
            error_msg = str(e)
            errors = [
                {
                    "line": 0,
                    "column": 0,
                    "message": error_msg,
                    "severity": "error",
                }
            ]
            return False, errors

    @staticmethod
    async def render_document(
        db: AsyncSession,
        redis: Optional[Redis],
        document_id: UUID,
        user_id: UUID,
        format: str = "html",
        use_cache: bool = True,
    ) -> Optional[str]:
        """
        Render a stored document

        Args:
            db: Database session
            redis: Redis client
            document_id: Document ID to render
            user_id: User ID (for ownership check)
            format: Output format ("html" or "markdown")
            use_cache: Whether to use cached render from database

        Returns:
            Rendered content or None if document not found
        """
        # Get document
        document = await DocumentService.get_document(db, document_id, user_id)
        if not document:
            return None

        # Check if we have a cached render in the database
        if use_cache:
            if format == "html" and document.rendered_html:
                return document.rendered_html
            elif format == "markdown" and document.rendered_markdown:
                return document.rendered_markdown

        # Render the document
        rendered, _ = await RenderService.render_pymd(
            content=document.content,
            format=format,
            redis=redis,
        )

        # Update cached render in database
        await DocumentService.update_cached_render(
            db=db,
            document_id=document_id,
            format=format,
            rendered_content=rendered,
        )

        return rendered

    @staticmethod
    async def clear_render_cache(
        redis: Redis,
        content: Optional[str] = None,
    ) -> int:
        """
        Clear render cache

        Args:
            redis: Redis client
            content: Optional specific content to clear cache for
                    If None, clears all render caches

        Returns:
            Number of keys deleted
        """
        if content:
            # Clear cache for specific content
            deleted = 0
            for format in ["html", "markdown"]:
                cache_key = RenderService._compute_cache_key(content, format)
                if await redis.delete(cache_key):
                    deleted += 1
            return deleted
        else:
            # Clear all render caches
            pattern = f"{RenderService.CACHE_PREFIX}*"
            keys = []
            async for key in redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await redis.delete(*keys)
            return 0
