from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr

from db.actions.course import find_course_by_canvas_id
from db.actions.message import all_messages_in_chat
from http_api.auth import get_current_session
from db.actions.chat import find_chat_by_id
from db.models import Chat, Session, Message


router = APIRouter()


class ChatResponse(BaseModel):
    public_id: str


class MessageResponse(BaseModel):
    message_id: str
    content: str
    sender: str
    created_at: str


class MessagesResponse(BaseModel):
    messages: List[MessageResponse]


class MessageRequestBody(BaseModel):
    content: constr(min_length=1, max_length=2048)


@router.post('/course/{course_canvas_id}/chat', dependencies=[Depends(get_current_session)], response_model=ChatResponse)
async def start_new_chat(course_canvas_id: str, session: Session = Depends(get_current_session)) -> ChatResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = Chat(course=course, session=session)
    chat.save()

    return ChatResponse(public_id=chat.public_id)


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

    return MessageResponse(
        message_id=msg.message_id,
        content=msg.content,
        sender=msg.sender,
        created_at=str(msg.created_at),
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
        out.append(MessageResponse(
            message_id=msg.message_id,
            content=msg.content,
            sender=msg.sender,
            created_at=str(msg.created_at),
        ))

    return MessagesResponse(messages=out)
