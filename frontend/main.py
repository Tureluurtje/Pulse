# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from typing import Union

app = FastAPI()

# Templates and static files
templates = Jinja2Templates(directory="templates")
app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

# Simple in-memory session storage (for demo only)
sessions: dict[str, str] = {}

API_URL = "http://localhost:10001"  # Change if your API runs elsewhere

# Index page
@app.get(path="/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Login page
@app.get(path="/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(name="login.html", context={"request": request, "error": None})

@app.post(path="/login")
async def login(
    request: Request, 
    email: str = Form(...), 
    password: str = Form(...)
) -> Union[RedirectResponse, HTMLResponse]:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url=f"{API_URL}/auth/login", 
                json={"email": email, "password": password}
            )
            response.raise_for_status()
            data = response.json()
            access_token = data["access_token"]
            # Simple session
            sessions[email] = access_token
            resp = RedirectResponse(url="/dashboard", status_code=302)
            resp.set_cookie(key="user_email", value=email)
            return resp
        except httpx.HTTPStatusError:
            return templates.TemplateResponse(
                name="login.html", 
                context={"request": request, "error": "Invalid credentials"}
            )

# Protected route
@app.get(path="/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> Union[RedirectResponse, HTMLResponse]:
    email = request.cookies.get("user_email")
    if not email or email not in sessions:
        return RedirectResponse(url="/login", status_code=302)

    token: str = sessions[email]
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f"{API_URL}/auth/validate", 
            json={"access_token": token}
        )
        if response.status_code != 200:
            return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        name="dashboard.html", 
        context={"request": request, "email": email}
    )