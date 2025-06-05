# app/middleware/token_refresh.py
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from datetime import datetime
from app.config import settings
from app import oauth2


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Routes that should get automatic token refresh
        self.web_routes = [
            "/staff",
            "/dashboard",
            "/web/locations",
            "/web/machines",
            "/web/dashboard"
        ]

    async def dispatch(self, request: Request, call_next):
        # Initialize token expiration data for web routes
        if self._is_web_route(request):
            token = request.cookies.get("access_token")
            if token:
                try:
                    # Decode the current token
                    token_data = jwt.decode(token, settings.oauth2_secret_key, algorithms=[settings.oauth2_algorithm])

                    # Calculate current expiration time using UTC
                    exp_timestamp = token_data.get('exp')
                    current_timestamp = datetime.utcnow().timestamp()

                    # Create new token with refreshed expiration
                    new_token = oauth2.create_web_token(data=token_data)

                    # Calculate NEW token expiration
                    new_token_data = jwt.decode(new_token, settings.oauth2_secret_key, algorithms=[settings.oauth2_algorithm])
                    new_exp_timestamp = new_token_data.get('exp')
                    new_seconds_until_expire = int(new_exp_timestamp - current_timestamp) if new_exp_timestamp else 0

                    # Store the NEW expiration time in request state
                    request.state.token_expires_in = max(0, new_seconds_until_expire)
                    request.state.new_token = new_token

                except JWTError:
                    request.state.token_expires_in = 0
                    request.state.new_token = None
                except Exception:
                    request.state.token_expires_in = 0
                    request.state.new_token = None
            else:
                request.state.token_expires_in = 0
                request.state.new_token = None

        # Process the request
        response: Response = await call_next(request)

        # Set the new token cookie if we have one
        if (self._is_web_route(request) and
            response.status_code == 200 and
            response.headers.get("content-type", "").startswith("text/html") and
            hasattr(request.state, 'new_token') and
            request.state.new_token):

            response.set_cookie(
                key="access_token",
                value=request.state.new_token,
                httponly=True,
                path="/",
                secure=False,
                samesite="Lax"
            )

        return response

    def _is_web_route(self, request: Request) -> bool:
        """Check if this is a web route that needs token refresh"""
        return any(request.url.path.startswith(route) for route in self.web_routes)