from fastapi import HTTPException, status, Security
from fastapi.security import APIKeyHeader
from db.models import Session

api_key_header = APIKeyHeader(name='X-Session-ID', auto_error=False)


async def get_current_session(session_id: str = Security(api_key_header)) -> Session:
    try:
        session = Session.get(Session.public_id == session_id, Session.is_valid is True)
        return session
    except Session.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session or session expired",
        )
