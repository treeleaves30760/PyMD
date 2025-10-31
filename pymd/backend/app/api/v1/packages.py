"""Package API endpoints"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pymd.backend.app.core.database import get_db
from pymd.backend.app.core.security import get_current_user
from pymd.backend.app.models.user import User
from pymd.backend.app.schemas.environment import (
    PackageInstallRequest,
    PackageInstallResponse,
    PackageResponse,
    PackageListResponse,
    RequirementsImportRequest,
    RequirementsImportResponse,
)
from pymd.backend.app.services.package_service import (
    PackageService,
    PackageQuotaExceededError,
    PackageNotFoundError,
    PackageServiceError,
)

router = APIRouter(prefix="/environments", tags=["packages"])


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
    "/{environment_id}/packages",
    response_model=PackageInstallResponse,
    status_code=status.HTTP_200_OK,
    summary="Install packages in an environment",
)
async def install_packages(
    environment_id: UUID,
    install_request: PackageInstallRequest,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Install one or more packages in an environment.

    - **packages**: List of package specifications (1-10 packages per request)
      - Examples: "numpy", "pandas==2.0.0", "flask>=2.0"

    Supports version pinning with operators: ==, >=, <=, ~=, !=

    **Response includes:**
    - success_count: Number of successfully installed packages
    - fail_count: Number of failed installations
    - successful: List of successfully installed packages with details
    - failed: List of failed packages with error messages

    **Quota limits:**
    - FREE tier: 50 packages per environment
    - PRO tier: 500 packages per environment

    **Notes:**
    - Installation is synchronous with a 5-minute timeout
    - Packages are installed using pip in an isolated Docker container
    - Already installed packages will be skipped
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    try:
        package_service = PackageService()
        successful, failed = await package_service.install_packages(
            environment_id=environment_id,
            packages=install_request.packages,
            user_id=user.id,
            db=db,
        )

        return PackageInstallResponse(
            success_count=len(successful),
            fail_count=len(failed),
            successful=successful,
            failed=failed,
        )

    except PackageQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except PackageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{environment_id}/packages",
    response_model=PackageListResponse,
    summary="List packages in an environment",
)
async def list_packages(
    environment_id: UUID,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all packages installed in an environment.

    Returns:
    - List of installed packages with name, version, size, and installation date
    - Total package count
    - Total size in bytes

    Only the environment owner can access this endpoint.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    try:
        package_service = PackageService()
        packages = await package_service.list_packages(
            environment_id=environment_id,
            user_id=user.id,
            db=db,
        )

        total_size = sum(pkg.size_bytes or 0 for pkg in packages)

        return PackageListResponse(
            packages=packages,
            total=len(packages),
            total_size_bytes=total_size,
        )

    except PackageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/{environment_id}/packages/{package_name}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Uninstall a package",
)
async def uninstall_package(
    environment_id: UUID,
    package_name: str,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Uninstall a package from an environment.

    - **package_name**: Name of the package to uninstall (case-sensitive)

    This will:
    - Remove the package from the Docker volume using pip uninstall
    - Delete the package record from the database
    - Update environment statistics (package count, total size)

    Returns 404 if the package is not found.
    Only the environment owner can uninstall packages.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    try:
        package_service = PackageService()
        await package_service.uninstall_package(
            environment_id=environment_id,
            package_name=package_name,
            user_id=user.id,
            db=db,
        )

        return None

    except PackageNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except PackageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{environment_id}/packages/{package_name}",
    response_model=PackageResponse,
    summary="Get package information",
)
async def get_package_info(
    environment_id: UUID,
    package_name: str,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific package.

    Returns:
    - Package name
    - Installed version
    - Size in bytes
    - Installation date

    Returns 404 if the package is not found.
    Only the environment owner can access this endpoint.
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    try:
        package_service = PackageService()
        package = await package_service.get_package_info(
            environment_id=environment_id,
            package_name=package_name,
            user_id=user.id,
            db=db,
        )

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package {package_name} not found in environment",
            )

        return package

    except PackageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "/{environment_id}/packages/import",
    response_model=RequirementsImportResponse,
    status_code=status.HTTP_200_OK,
    summary="Import packages from requirements.txt",
)
async def import_requirements(
    environment_id: UUID,
    import_request: RequirementsImportRequest,
    auth0_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Import and install packages from a requirements.txt file.

    - **requirements**: Contents of requirements.txt file as a string

    **Supported formats:**
    - Package names: `numpy`
    - Version pinning: `pandas==2.0.0`
    - Version ranges: `flask>=2.0,<3.0`
    - Comments: `# This is a comment`
    - Empty lines are ignored

    **Unsupported (will be skipped with warning):**
    - Editable installs: `-e git+https://...`
    - Recursive requirements: `-r other-requirements.txt`

    **Response includes:**
    - success_count: Number of successfully installed packages
    - fail_count: Number of failed installations
    - successful: List of successfully installed packages
    - failed: List of failed packages with error messages

    **Notes:**
    - Quota limits still apply
    - Each package is installed sequentially
    - Already installed packages will be skipped
    """
    user = await get_user_from_auth0_id(auth0_id, db)

    try:
        package_service = PackageService()
        success_count, fail_count, details = await package_service.import_requirements(
            environment_id=environment_id,
            requirements_txt=import_request.requirements,
            user_id=user.id,
            db=db,
        )

        return RequirementsImportResponse(
            success_count=success_count,
            fail_count=fail_count,
            successful=details.get("successful", []),
            failed=details.get("failed", []),
        )

    except PackageQuotaExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    except PackageServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
