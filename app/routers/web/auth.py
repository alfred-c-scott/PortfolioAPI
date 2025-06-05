from fastapi import status
from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import oauth2
from app.database import get_db
from app import utils


router = APIRouter(
    tags=["Web Authentication"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get('/login', response_class=HTMLResponse)
async def web_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post('/login', response_class=HTMLResponse)
async def login(request: Request,
                staff_credentials: OAuth2PasswordRequestForm = Depends(),
                db: Session = Depends(get_db)):

    staff = db.query(models.Staff).filter(models.Staff.email == staff_credentials.username).first()

    if not staff:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    if not utils.verify(staff_credentials.password, staff.password):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

    data = schemas.StaffTokenData.model_validate(staff).model_dump()

    access_token = oauth2.create_web_token(data=data)

    response = RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        path="/",
        secure=False,  # For local testing
        samesite="Lax"
    )
    return response


@router.get('/logout', response_class=HTMLResponse)
async def web_logout(request: Request):
    # Create redirect response to login page
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    # Clear the access_token cookie by setting it to expire immediately
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        secure=False,  # Match the secure setting from login
        samesite="Lax"
    )

    return response