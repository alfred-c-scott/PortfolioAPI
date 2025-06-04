from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/web/machines",
    tags=["Web Machines"],
)

templates = Jinja2Templates(directory="app/templates")
