from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@router.get(
    "/login",
    response_class=HTMLResponse
)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@router.get(
    "/register",
    response_class=HTMLResponse
)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


@router.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


@router.get(
    "/planner/{planner}",
    response_class=HTMLResponse
)
def planner_page(
    request: Request,
    planner: str
):

    allowed_planners = {
        "home",
        "party",
        "jewelry"
    }

    if planner not in allowed_planners:

        planner = "home"


    return templates.TemplateResponse(
        request=request,
        name=f"{planner}.html"
    )


@router.get(
    "/history",
    response_class=HTMLResponse
)
def history_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="history.html"
    )