# installed
from fastapi import Depends
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

# local
from app import oauth2

router = APIRouter(
    prefix="/staff",
    tags=["Web Staff"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get('', response_class=HTMLResponse)
async def staff(request: Request,
                current_user: int = Depends(oauth2.web_staff)):
    print(current_user)
    # print(request.headers)

    context = dict()
    context['request'] = request
    context['staff'] = current_user['token_data']

    response = templates.TemplateResponse("staff.html", context)

    response.set_cookie(
        key="access_token",
        value=current_user['new_token'],  # This is the refreshed token from web_staff
        httponly=True,
        path="/",
        secure=False,  # For local testing
        samesite="Lax"
    )

    return response
