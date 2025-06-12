# app/routers/web/staff.py
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
                db: Session = Depends(get_db),
                current_user: dict = Depends(oauth2.web_staff)):
    try:
        # Get token expiration from request state (set by middleware)
        token_expires_in = getattr(request.state, 'token_expires_in', 0)

        staff = db.query(models.Staff).all()
        # print(staff)

        context = {
            'request': request,
            'current_user': current_user,  # Current user for navbar/permissions
            'staff': staff,                # All staff members for table display
            'success': success,
            'token_expires_in': token_expires_in
        }

        return templates.TemplateResponse("staff.html", context)

    except Exception as e:
        return RedirectResponse(url="/login?error=page_load_failed", status_code=status.HTTP_302_FOUND)


@router.get('/add_staff', response_class=HTMLResponse)
async def add_staff_page(request: Request,
                         current_user: dict = Depends(oauth2.web_staff)):
    try:
        # Get token expiration from request state (set by middleware)
        token_expires_in = getattr(request.state, 'token_expires_in', 0)

        context = {
            'request': request,
            'current_user': current_user,
            'token_expires_in': token_expires_in
        }

        return templates.TemplateResponse("add_staff.html", context)

    except Exception as e:
        return RedirectResponse(url="/login?error=page_load_failed", status_code=status.HTTP_302_FOUND)


@router.post('/add_staff', response_class=HTMLResponse)
async def create_staff(
    request: Request,
    first_name: str = Form(...),
    middle_name: str = Form(""),
    last_name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    # password: str = Form(...),
    is_active: bool = Form(False),
    is_staff: bool = Form(False),
    is_tech: bool = Form(False),
    is_manager: bool = Form(False),
    is_admin: bool = Form(False),
    is_superuser: bool = Form(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(oauth2.web_staff)):

    try:
        # Server-side permission validation - only superusers can grant manager/superuser permissions
        if not current_user['is_superuser']:
            is_manager = False
            is_superuser = False

        # Create staff data dict
        staff_data = {
            "first_name": first_name,
            "middle_name": middle_name if middle_name else None,
            "last_name": last_name,
            "username": username,
            "email": email,
            "phone": phone,
            "password": utils.hash("password123"),  # Hash the password
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

        # Get token expiration for error response
        token_expires_in = getattr(request.state, 'token_expires_in', 0)

        # Return to add_staff page with error - middleware will handle token refresh
        context = {
            "request": request,
            "current_user": current_user,
            "error": error_message,
            "token_expires_in": token_expires_in
        }

        return templates.TemplateResponse("add_staff.html", context)

    except Exception as e:
        db.rollback()
        # Log the error if you have logging set up
        # logger.error(f"Error creating staff member: {str(e)}")

        # Get token expiration for error response
        token_expires_in = getattr(request.state, 'token_expires_in', 0)

        # Handle unexpected errors - middleware will handle token refresh
        context = {
            "request": request,
            "current_user": current_user,
            "error": "An unexpected error occurred while creating the staff member",
            "token_expires_in": token_expires_in
        }

        return templates.TemplateResponse("add_staff.html", context)


@router.get('/{staff_id}', response_class=HTMLResponse)
async def staff_member(request: Request,
                       staff_id: int,
                       success: str = None,  # Query parameter for success messages
                       error: str = None,    # Query parameter for error messages
                       db: Session = Depends(get_db),
                       current_user: dict = Depends(oauth2.web_staff)):

    try:
        staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()

        if not staff:
            return RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)

        token_expires_in = getattr(request.state, 'token_expires_in', 0)

        context = {
            'request': request,
            'current_user': current_user,
            'staff': staff,
            'token_expires_in': token_expires_in,
            'success': success,  # Pass success message to template
            'error': error       # Pass error message to template
        }

        return templates.TemplateResponse(request=request, name="staff_member.html", context=context)

    except Exception as e:
        return RedirectResponse(url="/login?error=page_load_failed", status_code=status.HTTP_302_FOUND)


@router.post('/{staff_id}/activate', response_class=HTMLResponse)
async def activate_staff(request: Request,
                        staff_id: int,
                        db: Session = Depends(get_db),
                        current_user: dict = Depends(oauth2.web_staff)):
    try:
        staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()

        if not staff:
            return RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)

        staff.password = utils.hash('password123')
        staff.staff_reset = False
        staff.is_active = True
        db.commit()

        return RedirectResponse(url=f"/staff/{staff_id}?success=activated",
                              status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/staff/{staff_id}?error=activation_failed",
                              status_code=status.HTTP_302_FOUND)


@router.post('/{staff_id}/deactivate', response_class=HTMLResponse)
async def deactivate_staff(request: Request,
                          staff_id: int,
                          db: Session = Depends(get_db),
                          current_user: dict = Depends(oauth2.web_staff)):
    try:
        staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()

        if not staff:
            return RedirectResponse(url="/staff", status_code=status.HTTP_302_FOUND)

        staff.password = utils.hash('password123')
        staff.staff_reset = True
        staff.is_active = False
        db.commit()

        return RedirectResponse(url=f"/staff/{staff_id}?success=deactivated",
                              status_code=status.HTTP_303_SEE_OTHER)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/staff/{staff_id}?error=deactivation_failed",
                              status_code=status.HTTP_302_FOUND)