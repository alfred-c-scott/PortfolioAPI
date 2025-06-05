# app/middleware/token_refresh.py
from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from app.config import settings
from app import oauth2


class TokenRefreshMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # Routes that should get automatic token refresh
        self.web_routes = [
            "/staff",
            "/web/locations",
            "/web/machines",
            "/web/dashboard"
        ]

    async def dispatch(self, request: Request, call_next):
        # Process the request
        response: Response = await call_next(request)

        # Only handle web routes that return HTML
        if self._should_refresh_token(request, response):
            token = request.cookies.get("access_token")

            if token:
                try:
                    # Decode current token to get user data
                    token_data = jwt.decode(token, settings.oauth2_secret_key, algorithms=[settings.oauth2_algorithm])

                    # DEBUG: Print current token info
                    print("-" * 70)
                    print(f"User:         {token_data.get('first_name')} {token_data.get('last_name')}")
                    print(f"Route:        {request.url.path}")
                    print(f"is_active:    {token_data.get('is_active', False)}")
                    print(f"is_staff:     {token_data.get('is_staff', False)}")
                    print(f"is_tech:      {token_data.get('is_tech', False)}")
                    print(f"is_manager:   {token_data.get('is_manager', False)}")
                    print(f"is_admin:     {token_data.get('is_admin', False)}")
                    print(f"is_superuser: {token_data.get('is_superuser', False)}")
                    print(f"Old Token:    {token[:50]}...")  # First 50 chars

                    # Create new token with refreshed expiration
                    new_token = oauth2.create_web_token(data=token_data)

                    # DEBUG: Print new token
                    print(f"New Token:    {new_token[:50]}...")
                    print("-" * 70)

                    # Set the new token cookie
                    response.set_cookie(
                        key="access_token",
                        value=new_token,
                        httponly=True,
                        path="/",
                        secure=False,
                        samesite="Lax"
                    )
                except JWTError:
                    # Token is invalid - let the auth middleware handle this
                    pass

        return response

    def _should_refresh_token(self, request: Request, response: Response) -> bool:
        """Determine if we should refresh the token for this request/response"""

        # Check if it's a web route
        is_web_route = any(request.url.path.startswith(route) for route in self.web_routes)

        # Check if response is HTML (status 200 and content-type contains text/html)
        is_html_response = (
            response.status_code == 200 and
            response.headers.get("content-type", "").startswith("text/html")
        )

        return is_web_route and is_html_response