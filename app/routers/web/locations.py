from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/web/locations",
    tags=["Web Locations"],
)

templates = Jinja2Templates(directory="app/templates")
