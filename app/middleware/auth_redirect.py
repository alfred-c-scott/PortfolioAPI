# app/middleware/auth_redirect.py
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import settings


class TokenExpirationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.protected_routes = [
            "/staff",
            "/dashboard",
        ]
        # Routes that should be excluded from token checking
        self.excluded_routes = [
            "/login",
            "/logout",
            "/api/",  # All API routes
            "/",      # Home page
            "/static/",  # Static files
        ]

    async def dispatch(self, request: Request, call_next):
        # Check if this is a web route that needs authentication
        if self._should_check_token(request.url.path):
            token = request.cookies.get("access_token")

            # No token present - redirect to login
            if not token:
                return RedirectResponse(url="/login", status_code=302)

            # Verify token
            try:
                jwt.decode(token, settings.oauth2_secret_key, algorithms=[settings.oauth2_algorithm])
            except JWTError:
                # Token is invalid/expired - redirect to login with expired flag
                return RedirectResponse(url="/login?expired=true", status_code=302)

        # Token is valid or route doesn't need auth - continue with request
        response = await call_next(request)
        return response

    def _should_check_token(self, path: str) -> bool:
        """Determine if the request path requires token validation"""

        # Skip excluded routes
        for excluded in self.excluded_routes:
            if path.startswith(excluded):
                return False

        # Check protected routes
        for protected in self.protected_routes:
            if path.startswith(protected):
                return True

        return False