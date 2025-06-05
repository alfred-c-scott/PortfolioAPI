# installed
from fastapi import Depends, Form, status
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation

# local
from app import oauth2, models, utils
from app.database import get_db

router = APIRouter(
    prefix="/staff",
    tags=["Web Staff"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get('', response_class=HTMLResponse)
async def staff(request: Request,
                success: bool = False,
                current_user: dict = Depends(oauth2.web_staff)):
    try:
        context = {
            'request': request,
            'staff': current_user['token_data'],
            'success': success
        }

        response = templates.TemplateResponse("staff.html", context)
        response.set_cookie(
            key="access_token",
            value=current_user['new_token'],
            httponly=True,
            path="/",
            secure=False,
            samesite="Lax"
        )
        return response

    except Exception as e:
        return RedirectResponse(url="/login?error=page_load_failed", status_code=status.HTTP_302_FOUND)


@router.post('', response_class=HTMLResponse)
async def create_staff(
    request: Request,
    first_name: str = Form(...),
    middle_name: str = Form(""),
    last_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    is_active: bool = Form(False),
    is_staff: bool = Form(False),
    is_tech: bool = Form(False),
    is_manager: bool = Form(False),
    is_admin: bool = Form(False),
    is_superuser: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.web_staff)):

    try:
        # Create staff data dict
        staff_data = {
            "first_name": first_name,
            "middle_name": middle_name if middle_name else None,
            "last_name": last_name,
            "username": username,
            "email": email,
            "phone": phone,
            "password": utils.hash(password),  # Hash the password
            "is_active": is_active,
            "is_staff": is_staff,
            "is_tech": is_tech,
            "is_manager": is_manager,
            "is_admin": is_admin,
            "is_superuser": is_superuser
        }

        # Create new staff member
        new_staff = models.Staff(**staff_data)
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)

        # Success - redirect back to staff page with success message
        return RedirectResponse(url="/staff?success=true", status_code=status.HTTP_303_SEE_OTHER)

    except IntegrityError as e:
        db.rollback()
        error_message = "Staff member could not be created"

        if isinstance(e.orig, UniqueViolation):
            error_detail = str(e.orig).lower()
            if "username" in error_detail:
                error_message = "Username already exists"
            elif "email" in error_detail:
                error_message = "Email already exists"
            elif "phone" in error_detail:
                error_message = "Phone number already exists"
            else:
                error_message = "Duplicate entry detected"

        # Return to staff page with error
        context = {
            "request": request,
            "staff": current_user['token_data'],
            "error": error_message
        }

        response = templates.TemplateResponse("staff.html", context)
        response.set_cookie(
            key="access_token",
            value=current_user['new_token'],
            httponly=True,
            path="/",
            secure=False,
            samesite="Lax"
        )
        return response

    except Exception as e:
        db.rollback()
        # Log the error if you have logging set up
        # logger.error(f"Error creating staff member: {str(e)}")

        # Handle unexpected errors
        context = {
            "request": request,
            "staff": current_user['token_data'],
            "error": "An unexpected error occurred while creating the staff member"
        }

        response = templates.TemplateResponse("staff.html", context)
        response.set_cookie(
            key="access_token",
            value=current_user['new_token'],
            httponly=True,
            path="/",
            secure=False,
            samesite="Lax"
        )
        return response