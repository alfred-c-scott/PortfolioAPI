# app/main.py
# installed
from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from sqlalchemy.orm import Session

# local
from app.middleware.no_cache import NoCacheMiddleware
from app.middleware.token_refresh import TokenRefreshMiddleware
from app.middleware.auth_redirect import TokenExpirationMiddleware

from app.routers.api import auth as api_auth
from app.routers.api import locations as api_locations
from app.routers.api import machines as api_machines
from app.routers.api import customer as api_customer

from app.routers.web import auth as web_auth
# from app.routers.web import projects
from app.routers.web import staff as web_staff
from app.routers.web import dashboard as web_dashboard
# from app.routers.web import locations as web_locations
# from app.routers.web import machines as web_machines

templates = Jinja2Templates(directory="app/templates")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add before other middleware
app.add_middleware(NoCacheMiddleware)
# Order matters! Token refresh should happen AFTER auth check but BEFORE response
app.add_middleware(TokenRefreshMiddleware)     # Second - handles token refresh
app.add_middleware(TokenExpirationMiddleware)  # First - handles authentication

app.include_router(api_auth.router)
app.include_router(api_locations.router)
app.include_router(api_machines.router)
app.include_router(api_customer.router)

app.include_router(web_auth.router)
# app.include_router(projects.router)
app.include_router(web_staff.router)
app.include_router(web_dashboard.router)
# app.include_router(web_locations.router)
# app.include_router(web_machines.router)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"msg": exc.detail, "status_code": exc.status_code}}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):

    errors = exc.errors()
    simplified_errors = []

    for error in errors:
        msg = error["msg"]

        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]

        if "PIN must be 4 digits" in msg:
            msg = "PIN must be 4 digits"
        elif "Invalid phone number" in msg:
            msg = "Phone number must be exactly 10 digits"

        simplified_errors.append(msg)

    error_msg = "; ".join(simplified_errors)
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    return JSONResponse(
        status_code=status_code,
        content={"error": {"msg": error_msg, "status_code": status_code}}
    )


@app.exception_handler(HTTPException)
async def auth_exception_handler(request: Request, exc: HTTPException):
    # Check if this is a 401 error on a web route (not API)
    if exc.status_code == 401 and not request.url.path.startswith("/api/"):
        # Check if it's an authentication error
        if "Could not validate credentials" in str(exc.detail) or "Not authenticated" in str(exc.detail):
            return RedirectResponse(url="/login?expired=true", status_code=302)

    # For all other cases, use the existing JSON response
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"msg": exc.detail, "status_code": exc.status_code}}
    )