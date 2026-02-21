from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/otp", response_class=HTMLResponse)
def otp_page(request: Request):
    return templates.TemplateResponse("otp.html", {"request": request})


@router.get("/vote", response_class=HTMLResponse)
def vote_page(request: Request):
    return templates.TemplateResponse("vote.html", {"request": request})


@router.get("/receipt", response_class=HTMLResponse)
def receipt_page(request: Request):
    return templates.TemplateResponse("receipt.html", {"request": request})


@router.get("/admin", response_class=HTMLResponse)
def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})
