import os
import sys
import asyncio
from typing import Callable, Awaitable

# When running the file directly (for example from the `api/` folder in a debugger)
# Python's import machinery won't find the top-level `api` package because
# sys.path[0] is the `api/` directory. Add the project root to sys.path so
# absolute imports like `import api.routes` work regardless of CWD.
if __package__ is None:
    # When running this file directly we need to make relative imports work.
    # Add the project root to sys.path and set __package__ so package-relative
    # imports (from . import ...) resolve correctly without using absolute imports.
    project_root = os.path.dirname(p=os.path.dirname(p=os.path.abspath(path=__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    # Set package for relative imports
    __package__ = "api"

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from .routes import (
    auth as auth_routes,
    users as users_routes,
    messages as messages_routes,
    conversations as conversations_routes,
)
from .sockets import auth_socket_router, chat_socket_router
from .services.auth_service import cleanup_tokens

# Define main app function config
app = FastAPI()

# Set CORS
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],     # Allow GET, POST, etc.
    allow_headers=["*"],     # Allow custom headers
)

# Define routers
# Include API routers from the routes package (each module exposes an APIRouter
# instance named `router`). Import names are aliased above to avoid shadowing
# module names with local symbols.
app.include_router(router=auth_routes.router)
app.include_router(router=users_routes.router)
app.include_router(router=messages_routes.router)
app.include_router(router=conversations_routes.router)

# Define websockets
app.include_router(router=auth_socket_router)
app.include_router(router=chat_socket_router)

@app.middleware(middleware_type="http")
async def cleanup_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    # Fire-and-forget token cleanup; don't await so requests aren't delayed.
    asyncio.create_task(cleanup_tokens())
    response: Response = await call_next(request)
    return response

@app.get(path="/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}
