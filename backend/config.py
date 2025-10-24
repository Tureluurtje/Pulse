"""Application configuration loaded from environment.

This module reads configuration from environment variables. During local
development a root-level ``.env`` file is loaded (via python-dotenv) so that
values can be kept out of source control while maintaining sensible defaults.

The expected environment variables are documented in the repository-level
``.env`` file.
"""
from os import environ
from pathlib import Path
from dotenv import load_dotenv

# Load root .env if present (project root). Use parent directories to be robust
ROOT = Path(__file__).resolve().parents[1]
dotenv_path = ROOT / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# Database config
DB = {
    "USERNAME": environ.get("DB_USERNAME", "postgres"),
    "***REMOVED***": environ.get("DB_***REMOVED***", "***REMOVED***"),
    "DATABASE": environ.get("DB_DATABASE", "pulse"),
}

# Auth / JWT settings
***REMOVED*** = environ.get("***REMOVED***", "supersecret")
ALGORITHM = environ.get("ALGORITHM", "HS256")
_access_default = environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
try:
    _access_value = int(_access_default)
except ValueError:
    _access_value = 15
ACCESS_TOKEN_EXPIRE_MINUTES = _access_value

_refresh_default = environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "30")
try:
    _refresh_value = int(_refresh_default)
except ValueError:
    _refresh_value = 30
REFRESH_TOKEN_EXPIRE_DAYS = _refresh_value
