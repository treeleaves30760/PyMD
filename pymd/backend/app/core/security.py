"""Security utilities and JWT validation"""
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

from pymd.backend.app.config import settings

security = HTTPBearer()


class AuthMiddleware:
    """Auth0 JWT validation middleware"""

    def __init__(self):
        self.auth0_domain = settings.AUTH0_DOMAIN
        self.client_id = settings.AUTH0_CLIENT_ID
        self.algorithms = settings.AUTH0_ALGORITHMS
        self.jwks_url = f"https://{self.auth0_domain}/.well-known/jwks.json"
        self._jwks_cache: Optional[Dict] = None
        self._jwks_cache_time: Optional[datetime] = None

    async def get_jwks(self) -> Dict:
        """Get JWKS (JSON Web Key Set) for token verification with caching"""
        # Cache JWKS for 1 hour
        if (
            self._jwks_cache
            and self._jwks_cache_time
            and datetime.utcnow() - self._jwks_cache_time < timedelta(hours=1)
        ):
            return self._jwks_cache

        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url, timeout=10.0)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_cache_time = datetime.utcnow()
            return self._jwks_cache

    def _get_rsa_key(self, jwks: Dict, kid: str) -> Dict:
        """Extract RSA key from JWKS"""
        for key in jwks.get("keys", []):
            if key["kid"] == kid:
                return {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        return {}

    async def verify_token(
        self, credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """Verify JWT token and return claims"""
        token = credentials.credentials

        try:
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing key ID",
                )

            # Get signing key from JWKS
            jwks = await self.get_jwks()
            rsa_key = self._get_rsa_key(jwks, kid)

            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate signing key",
                )

            # Verify token (using client_id as audience for Regular Web Applications)
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=self.algorithms,
                audience=self.client_id,
                issuer=f"https://{self.auth0_domain}/",
            )

            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to verify token: {str(e)}",
            )


# Global auth middleware instance
auth_middleware = AuthMiddleware()


async def get_current_user(token_payload: Dict = Depends(auth_middleware.verify_token)) -> str:
    """Get current user ID from verified token"""
    user_id = token_payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject",
        )
    return user_id


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[str]:
    """Get current user ID if authenticated, None otherwise"""
    if not credentials:
        return None
    try:
        token_payload = await auth_middleware.verify_token(credentials)
        return token_payload.get("sub")
    except HTTPException:
        return None
