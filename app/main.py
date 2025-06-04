# installed
from fastapi import FastAPI
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from sqlalchemy.orm import Session

# local
from app.middleware.auth import TokenExpirationMiddleware

from app.routers.api import auth as api_auth
from app.routers.api import locations as api_locations
from app.routers.api import machines as api_machines
from app.routers.api import customer as api_customer

from app.routers.web import auth as web_auth
from app.routers.web import staff as web_staff
from app.routers.web import locations as web_locations
from app.routers.web import machines as web_machines

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

app.add_middleware(TokenExpirationMiddleware)

app.include_router(api_auth.router)
app.include_router(api_locations.router)
app.include_router(api_machines.router)
app.include_router(api_customer.router)

app.include_router(web_auth.router)
app.include_router(web_staff.router)
app.include_router(web_locations.router)
app.include_router(web_machines.router)


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
