from fastapi import APIRouter, Depends
from pydantic import BaseModel

from http_api.auth import get_current_session
from db.models import Session

router = APIRouter()


class SessionResponse(BaseModel):
    public_id: str


@router.post('/session', response_model=SessionResponse)
async def create_session() -> SessionResponse:
    session = Session()
    session.save()
    return SessionResponse(public_id=session.public_id)


@router.get('/session/me', dependencies=[Depends(get_current_session)])
async def get_current_session(session: Session = Depends(get_current_session)):
    return {
        'message': f"hello there your session is '{session.public_id}', it was started at {session.created_at}."
    }
