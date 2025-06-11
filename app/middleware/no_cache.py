# Create a new file: app/middleware/no_cache.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import Response

class NoCacheMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)

        # Only add no-cache headers to web pages (HTML responses)
        if (not request.url.path.startswith("/api/") and
            response.headers.get("content-type", "").startswith("text/html")):

            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response