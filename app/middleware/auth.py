from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import settings

class TokenExpirationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Define protected path prefixes - any path starting with these will be protected
        self.protected_paths = [
            "/staff",           # Protects /staff, /staff/, /staff/1, /staff/dashboard, etc.
        ]
        self.login_path = "/login"
        # Paths that should be excluded from protection (even if they start with protected paths)
        self.excluded_paths = [
            "/login"
        ]

    def is_protected_path(self, path: str) -> bool:
        """
        Check if the given path should be protected.
        Returns True if path starts with any protected prefix and is not in excluded paths.
        """
        # First check if path is explicitly excluded
        if path in self.excluded_paths:
            return False

        # Check if path starts with any protected prefix
        return any(path.startswith(protected_path) for protected_path in self.protected_paths)

    async def dispatch(self, request: Request, call_next):
        # Check if this is a protected web route
        if self.is_protected_path(request.url.path):
            token = request.cookies.get("access_token")

            if not token:
                # Add query parameter to indicate session expiration
                return RedirectResponse(url=f"{self.login_path}?expired=true", status_code=302)

            try:
                # Verify token without dependency injection
                jwt.decode(token, settings.oauth2_secret_key, algorithms=[settings.oauth2_algorithm])
            except jwt.ExpiredSignatureError:
                # Token is expired, redirect to login
                response = RedirectResponse(url=f"{self.login_path}?expired=true", status_code=302)
                response.delete_cookie("access_token", path="/")
                return response
            except JWTError:
                # Token is invalid, redirect to login
                response = RedirectResponse(url=f"{self.login_path}?invalid=true", status_code=302)
                response.delete_cookie("access_token", path="/")
                return response

        response = await call_next(request)
        return response