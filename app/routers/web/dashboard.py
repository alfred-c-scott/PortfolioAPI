# app/routers/web/dashboard.py
from fastapi import Depends
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# local
from app import oauth2

router = APIRouter(
    prefix="/dashboard",
    tags=["Web Dashboard"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get('', response_class=HTMLResponse)
async def dashboard(request: Request,
                    current_user: dict = Depends(oauth2.web_staff)):
    try:
        # Get token expiration from request state (set by middleware)
        token_expires_in = getattr(request.state, 'token_expires_in', 0)

        context = {
            'request': request,
            'current_user': current_user,
            'token_expires_in': token_expires_in
        }

        return templates.TemplateResponse("dashboard.html", context)

    except Exception as e:
        from fastapi.responses import RedirectResponse
        from fastapi import status
        return RedirectResponse(url="/login?error=page_load_failed", status_code=status.HTTP_302_FOUND)