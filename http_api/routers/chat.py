from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr

from db.models import Chat, Session, Message, PromptHandle
from db.actions.course import find_course_by_canvas_id
from db.actions.message import all_messages_in_chat
from http_api.auth import get_current_session
from db.actions.chat import find_chat_by_id
from services.llm.llm import LLMService
import db.actions.chat_config

router = APIRouter()


class ChatResponse(BaseModel):
    public_id: str
    model_name: str


class MessageResponse(BaseModel):
    message_id: str
    content: Optional[str]
    sender: str
    streaming: bool
    websocket: Optional[str]
    created_at: str


class MessagesResponse(BaseModel):
    messages: List[MessageResponse]


class MessageRequestBody(BaseModel):
    content: constr(min_length=1, max_length=2048)


@router.post(
    '/course/{course_canvas_id}/chat',
    dependencies=[Depends(get_current_session)],
    response_model=ChatResponse
)
async def start_new_chat(course_canvas_id: str, session: Session = Depends(get_current_session)) -> ChatResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    config = db.actions.chat_config.get_random_chat_config()
    if config is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No valid chat config")

    chat = Chat(course=course, session=session, model_name=config.model_name)
    chat.save()

    return ChatResponse(public_id=chat.public_id, model_name=chat.model_name)


@router.post(
    '/course/{course_canvas_id}/chat/{chat_id}/messages',
    dependencies=[Depends(get_current_session)],
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse
)
async def send_message(
        course_canvas_id: str,
        chat_id: str,
        body: MessageRequestBody,
) -> MessageResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = find_chat_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    msg = Message(chat=chat, content=body.content, sender=Message.Sender.STUDENT)
    msg.save()

    handle = LLMService.dispatch_prompt(body.content, chat.model_name, chat.model_params)

    response_msg = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, prompt_handle=handle)
    response_msg.save()

    return MessageResponse(
        message_id=msg.message_id,
        content=msg.content,
        sender=msg.sender,
        created_at=str(msg.created_at),
        streaming=False,
        websocket=None,
    )


@router.get(
    '/course/{course_canvas_id}/chat/{chat_id}/messages',
    dependencies=[Depends(get_current_session)],
    status_code=status.HTTP_200_OK,
    response_model=MessagesResponse
)
async def get_messages(
        course_canvas_id: str,
        chat_id: str,
) -> MessagesResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = find_chat_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    messages = all_messages_in_chat(chat.id)
    out = []
    for msg in messages:
        streaming = False
        websocket = None
        content = msg.content
        if msg.prompt_handle:
            if msg.prompt_handle.state == PromptHandle.States.PENDING:
                streaming = True
                websocket = msg.prompt_handle.websocket_uri
                content = None
            elif msg.prompt_handle.state == PromptHandle.States.IN_PROGRESS:
                streaming = True
                websocket = msg.prompt_handle.websocket_uri
                content = None
            elif msg.prompt_handle.state == PromptHandle.States.FINISHED:
                streaming = False
                websocket = None
                content = msg.prompt_handle.response

        out.append(MessageResponse(
            message_id=msg.message_id,
            content=content,
            sender=msg.sender,
            created_at=str(msg.created_at),
            streaming=streaming,
            websocket=websocket,
        ))

    return MessagesResponse(messages=out)
