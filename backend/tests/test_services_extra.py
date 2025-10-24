from uuid import uuid4
from starlette.requests import Request as StarletteRequest
from starlette.datastructures import Headers
from starlette.types import Scope
from typing import Optional

from backend.services import auth_service as auth_svc
from backend.services import websocket_service as ws_svc

def make_request_with_auth(
    header_value: Optional[str] = None,
    query_token: Optional[str] = None,
) -> StarletteRequest:
    """
    Creates a fake Starlette Request with an Authorization header
    or token query param for testing auth functions.
    """
    # Build headers dictionary
    headers: dict[str, str] = {}
    if header_value is not None:
        headers["Authorization"] = header_value

    # Build query string
    query_string = b""
    if query_token is not None:
        query_string = f"token={query_token}".encode()

    # Build Starlette-compatible scope
    scope: Scope = {
        "type": "http",
        "headers": Headers(headers=headers).raw,
        "query_string": query_string,
    }

    return StarletteRequest(scope=scope)

def test_get_access_token_from_header_and_query() -> None:
    req = make_request_with_auth(header_value="Bearer abc.def.ghi")
    assert auth_svc.get_access_token(request=req) == "abc.def.ghi"

    req2 = make_request_with_auth(query_token="query-token-123")
    # no header so should return the query token
    assert auth_svc.get_access_token(request=req2) == "query-token-123"

def test_get_user_from_access_token_returns_sub() -> None:
    # create a simple access token payload via the helper
    temp_uuid = uuid4()
    tok = auth_svc.create_access_token(user_id=temp_uuid)
    req = make_request_with_auth(header_value=f"Bearer {tok}")
    # should return the subject (user id)
    user_id = auth_svc.get_user_from_access_token(request=req)
    assert user_id == temp_uuid

def test_generate_connection_id_unique() -> None:
    a = ws_svc.generate_connection_id()
    b = ws_svc.generate_connection_id()
    assert isinstance(a, str)
    assert isinstance(b, str)
    assert a != b
