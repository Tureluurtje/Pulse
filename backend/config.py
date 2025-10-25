"""Application configuration loaded from environment.

This module reads configuration from environment variables. During local
development a root-level ``.env`` file is loaded (via python-dotenv) so that
values can be kept out of source control while maintaining sensible defaults.

The expected environment variables are documented in the repository-level
``.env`` file.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load root .env if present (project root). Use parent directories to be robust
ROOT = Path(__file__).resolve().parents[1]
dotenv_path = ROOT / ".env"
if not dotenv_path.exists():
    raise FileNotFoundError(f".env file not found at {dotenv_path}")

load_dotenv(dotenv_path)

def require_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

# Database config
DB: dict[str, Optional[str]] = {
    "USERNAME": require_env("DB_USERNAME"),
    "***REMOVED***": require_env("DB_***REMOVED***"),
    "DATABASE": require_env("DB_DATABASE"),
}

# Auth / JWT settings
***REMOVED***: Optional[str] = require_env("***REMOVED***")
ALGORITHM: Optional[str] = require_env("ALGORITHM")

_access_default: str = require_env("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(_access_default)

_refresh_default = str = require_env("REFRESH_TOKEN_EXPIRE_DAYS", "30")
REFRESH_TOKEN_EXPIRE_DAYS = int(_refresh_default)
