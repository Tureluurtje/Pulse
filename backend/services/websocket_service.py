import uuid

def generate_connection_id() -> str:
    """Generate a new unique identifier for a WebSocket connection.

    Returns:
        A string UUID suitable for use as a connection identifier.
    """
    return str(uuid.uuid4())
