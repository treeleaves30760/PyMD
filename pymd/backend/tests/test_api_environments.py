"""Tests for Environment API endpoints"""
import pytest
import uuid
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import Mock, patch, AsyncMock

from pymd.backend.app.main import app
from pymd.backend.app.models.user import User, UserRole
from pymd.backend.app.models.environment import UserEnvironment, EnvironmentStatus


@pytest.fixture
def mock_user():
    """Create a mock user"""
    return User(
        id=uuid.uuid4(),
        auth0_id="auth0|test123",
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
    )


@pytest.fixture
def mock_environment(mock_user):
    """Create a mock environment"""
    return UserEnvironment(
        id=uuid.uuid4(),
        user_id=mock_user.id,
        name="test-env",
        python_version="3.11",
        volume_name=f"pymd-env-{mock_user.id}-test-env",
        status=EnvironmentStatus.ACTIVE,
        total_size_bytes=0,
        package_count=0,
    )


@pytest.mark.asyncio
class TestEnvironmentAPI:
    """Test Environment API endpoints"""

    async def test_create_environment_success(self, mock_user):
        """Test successful environment creation"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.create_environment") as mock_create:
                    # Mock the create_environment method
                    mock_env = UserEnvironment(
                        id=uuid.uuid4(),
                        user_id=mock_user.id,
                        name="new-env",
                        python_version="3.11",
                        volume_name=f"pymd-env-{mock_user.id}-new-env",
                        status=EnvironmentStatus.ACTIVE,
                        total_size_bytes=0,
                        package_count=0,
                    )
                    mock_create.return_value = mock_env

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.post(
                            "/api/v1/environments",
                            json={"name": "new-env", "python_version": "3.11"},
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 201
                    data = response.json()
                    assert data["name"] == "new-env"
                    assert data["python_version"] == "3.11"
                    assert data["status"] == "active"

    async def test_create_environment_quota_exceeded(self, mock_user):
        """Test environment creation when quota is exceeded"""
        from pymd.backend.app.services.environment_service import QuotaExceededError

        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.create_environment") as mock_create:
                    # Mock quota exceeded error
                    mock_create.side_effect = QuotaExceededError("Maximum 3 environments allowed")

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.post(
                            "/api/v1/environments",
                            json={"name": "new-env", "python_version": "3.11"},
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 409
                    data = response.json()
                    assert "quota" in data["detail"].lower() or "maximum" in data["detail"].lower()

    async def test_list_environments(self, mock_user, mock_environment):
        """Test listing user's environments"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.list_environments") as mock_list:
                    # Mock list_environments method
                    mock_list.return_value = [mock_environment]

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.get(
                            "/api/v1/environments",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert "environments" in data
                    assert len(data["environments"]) == 1
                    assert data["total"] == 1
                    assert data["environments"][0]["name"] == "test-env"

    async def test_get_environment_by_id(self, mock_user, mock_environment):
        """Test getting a specific environment by ID"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.get_environment") as mock_get:
                    # Mock get_environment method
                    mock_get.return_value = mock_environment

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.get(
                            f"/api/v1/environments/{mock_environment.id}",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["name"] == "test-env"
                    assert data["status"] == "active"

    async def test_get_environment_not_found(self, mock_user):
        """Test getting a non-existent environment"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.get_environment") as mock_get:
                    # Mock environment not found
                    mock_get.return_value = None

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.get(
                            f"/api/v1/environments/{uuid.uuid4()}",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 404

    async def test_update_environment(self, mock_user, mock_environment):
        """Test updating an environment"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.update_environment") as mock_update:
                    # Mock update_environment method
                    updated_env = UserEnvironment(**mock_environment.__dict__)
                    updated_env.name = "updated-env"
                    mock_update.return_value = updated_env

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.patch(
                            f"/api/v1/environments/{mock_environment.id}",
                            json={"name": "updated-env"},
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["name"] == "updated-env"

    async def test_reset_environment(self, mock_user, mock_environment):
        """Test resetting an environment"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.reset_environment") as mock_reset:
                    # Mock reset_environment method
                    reset_env = UserEnvironment(**mock_environment.__dict__)
                    reset_env.package_count = 0
                    reset_env.total_size_bytes = 0
                    mock_reset.return_value = reset_env

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.post(
                            f"/api/v1/environments/{mock_environment.id}/reset",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["package_count"] == 0
                    assert data["total_size_bytes"] == 0

    async def test_delete_environment(self, mock_user, mock_environment):
        """Test deleting an environment"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.delete_environment") as mock_delete:
                    # Mock delete_environment method
                    mock_delete.return_value = True

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.delete(
                            f"/api/v1/environments/{mock_environment.id}",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 204

    async def test_delete_environment_not_found(self, mock_user):
        """Test deleting a non-existent environment"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.delete_environment") as mock_delete:
                    # Mock delete failed
                    mock_delete.return_value = False

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.delete(
                            f"/api/v1/environments/{uuid.uuid4()}",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 404

    async def test_get_environment_stats(self, mock_user):
        """Test getting environment usage statistics"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                with patch("pymd.backend.app.services.environment_service.EnvironmentService.get_environment_stats") as mock_stats:
                    # Mock get_environment_stats method
                    mock_stats.return_value = {
                        "environment_count": 2,
                        "environment_limit": 10,
                        "total_size_bytes": 1048576,
                        "size_limit_bytes": 10737418240,
                        "total_packages": 15,
                        "package_limit": 500,
                        "can_create_environment": True,
                    }

                    async with AsyncClient(app=app, base_url="http://test") as client:
                        response = await client.get(
                            "/api/v1/environments/stats",
                            headers={"Authorization": "Bearer fake-token"},
                        )

                    assert response.status_code == 200
                    data = response.json()
                    assert data["environment_count"] == 2
                    assert data["environment_limit"] == 10
                    assert data["can_create_environment"] is True

    async def test_unauthorized_access(self):
        """Test accessing endpoints without authentication"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # No Authorization header
            response = await client.get("/api/v1/environments")
            assert response.status_code == 401

    async def test_create_environment_invalid_name(self, mock_user):
        """Test creating environment with invalid name"""
        with patch("pymd.backend.app.core.security.get_current_user", return_value=mock_user.auth0_id):
            with patch("pymd.backend.app.api.v1.environments.get_user_from_auth0_id", return_value=mock_user):
                async with AsyncClient(app=app, base_url="http://test") as client:
                    # Empty name
                    response = await client.post(
                        "/api/v1/environments",
                        json={"name": "", "python_version": "3.11"},
                        headers={"Authorization": "Bearer fake-token"},
                    )
                    assert response.status_code == 422

                    # Name too long
                    response = await client.post(
                        "/api/v1/environments",
                        json={"name": "a" * 101, "python_version": "3.11"},
                        headers={"Authorization": "Bearer fake-token"},
                    )
                    assert response.status_code == 422
