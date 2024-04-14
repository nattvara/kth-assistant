from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from http_api.auth import get_current_session
import db.actions.chat_config
from config.logger import log
from db.models import Session

router = APIRouter()


class SessionResponse(BaseModel):
    public_id: str
    message: str
    consent: bool


class ConsentRequestBody(BaseModel):
    granted: bool


class ConsentResponse(BaseModel):
    granted: bool


@router.post('/session', response_model=SessionResponse)
async def create_session() -> SessionResponse:
    config = db.actions.chat_config.get_random_chat_config()
    if config is None:
        raise HTTPException(status_code=500, detail="couldn't find a chat config to use as default")

    session = Session(
        default_llm_model_name=config.llm_model_name,
        default_index_type=config.index_type,
    )
    session.save()
    return SessionResponse(public_id=session.public_id, message="welcome.", consent=session.consent)


@router.get('/session/me', dependencies=[Depends(get_current_session)], response_model=SessionResponse)
async def return_current_session(session: Session = Depends(get_current_session)):
    return SessionResponse(
        public_id=session.public_id,
        consent=session.consent,
        message=f"hello there your session is '{session.public_id}', it was started at {session.created_at}.",
    )


@router.post('/session/consent', dependencies=[Depends(get_current_session)], response_model=ConsentResponse)
async def grant_consent(
    body: ConsentRequestBody,
    session: Session = Depends(get_current_session)
) -> ConsentResponse:
    if not body.granted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="consent can only be revoked by contacting the researcher."
        )

    log().info(f"user with session public_id {session.id} granted consent for study.")

    session.consent = body.granted
    session.save()
    return ConsentResponse(granted=session.consent)
