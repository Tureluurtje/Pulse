from fastapi import FastAPI, Request, APIRouter
import uvicorn

from routes import auth
from services.auth_service import cleanup_tokens

# Define main app function config
app = FastAPI()

# Define routers
router = APIRouter()
app.include_router(auth.router)

@app.middleware("http")
async def cleanup_middleware(request: Request, call_next):
    cleanup_tokens()  # Run cleanup before the request
    response = await call_next(request)  # Continue to the actual endpoint
    return response

@app.get("/")
def read_root():
    return {"Hello": "World"}

@router.get("/auth")
async def auth():
    return {"msg": "User Profile"}
