from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, constr

from db.actions.feedback import find_feedback_by_message_private_id
from db.actions.message import all_messages_in_chat, find_message_by_chat_private_id_and_message_public_id
from db.actions.course import find_course_by_canvas_id
from db.models import Session, Message, PromptHandle
from db.models.feedback import QUESTION_UNANSWERED
from services.chat.chat_service import ChatService
from db.actions.faq import find_faq_by_public_id
from http_api.auth import get_current_session
from db.actions.chat import find_chat_by_id
from config.logger import log

router = APIRouter()


class CourseResponse(BaseModel):
    canvas_id: str
    language: str
    name: str


class Faq(BaseModel):
    faq_id: str
    question: str


class ChatResponse(BaseModel):
    public_id: str
    llm_model_name: str
    index_type: str
    language: str
    course_name: str
    faqs: List[Faq]
    read_only: bool = False


class ChatModel(BaseModel):
    chat_id: str
    llm_model_name: str
    index_type: str
    user_id: str
    created_at: str


class ChatsResponse(BaseModel):
    chats: List[ChatModel]


class MessageResponse(BaseModel):
    message_id: str
    content: Optional[str]
    sender: str
    state: str
    streaming: bool
    websocket: Optional[str]
    created_at: str
    from_faq: bool
    feedback_id: Optional[str] = None


class MessagesResponse(BaseModel):
    messages: List[MessageResponse]


class MessageRequestBody(BaseModel):
    content: Optional[constr(min_length=1, max_length=2048)] = None
    faq_id: Optional[str] = None


@router.get(
    '/course/{course_canvas_id}',
    dependencies=[Depends(get_current_session)],
    response_model=CourseResponse
)
async def get_course_details(course_canvas_id: str) -> CourseResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    return CourseResponse(
        canvas_id=course.canvas_id,
        language=course.language,
        name=course.name,
    )


@router.post(
    '/course/{course_canvas_id}/chat',
    dependencies=[Depends(get_current_session)],
    response_model=ChatResponse
)
async def start_new_chat(course_canvas_id: str, session: Session = Depends(get_current_session)) -> ChatResponse:
    if not session.consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start a chat without granting consent."
        )

    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = ChatService.start_new_chat_for_session_and_course(session, course)

    snapshot = ChatService.get_most_recent_faq_snapshot(course)

    return ChatResponse(
        public_id=chat.public_id,
        llm_model_name=chat.llm_model_name,
        index_type=chat.index_type,
        language=chat.language,
        course_name=chat.course.name,
        faqs=[faq.to_dict() for faq in snapshot.faqs],
    )


@router.get(
    '/course/{course_canvas_id}/chat',
    dependencies=[Depends(get_current_session)],
    response_model=ChatsResponse
)
async def get_chats_in_course(course_canvas_id: str, session: Session = Depends(get_current_session)) -> ChatsResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if course.canvas_id not in session.admin_courses:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not admin for this course.")

    chats = []
    for chat in course.chats:
        if len(chat.messages) == 0:
            continue
        chats.append(ChatModel(
            chat_id=chat.public_id,
            llm_model_name=chat.llm_model_name,
            index_type=chat.index_type,
            user_id=chat.session.get_user_id(),
            created_at=str(chat.created_at)
        ))

    chats = sorted(chats, key=lambda c: c.created_at, reverse=True)

    return ChatsResponse(chats=chats)


@router.get(
    '/course/{course_canvas_id}/chat/{chat_id}',
    dependencies=[Depends(get_current_session)],
    response_model=ChatResponse
)
async def get_chat_details(
    course_canvas_id: str,
    chat_id: str,
    session: Session = Depends(get_current_session)
) -> ChatResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = find_chat_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    access = False
    read_only = False
    if course.canvas_id in session.admin_courses:
        log().warn(f"admin user {session.public_id} fetched chat details for chat {chat.public_id}")
        access = True
        if chat.session.id != session.id:
            read_only = True

    if not access and chat.session.id != session.id:
        log().warn("user tried to get chat thad didn't belong to the user")
    else:
        access = True

    if not access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    snapshot = ChatService.get_most_recent_faq_snapshot(course)

    return ChatResponse(
        public_id=chat.public_id,
        llm_model_name=chat.llm_model_name,
        index_type=chat.index_type,
        language=chat.language,
        course_name=chat.course.name,
        faqs=[faq.to_dict() for faq in snapshot.faqs],
        read_only=read_only
    )


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
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_current_session),
) -> MessageResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = find_chat_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    if chat.session.id != session.id:
        log().warn("user tried to send message in chat thad didn't belong to the user")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    if body.faq_id is None and body.content is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message must contain faq_id or content")

    if body.content is not None:
        content = body.content

    faq = None
    if body.faq_id is not None:
        faq = find_faq_by_public_id(body.faq_id)
        if faq is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FAQ not found")
        content = faq.question

    msg = Message(chat=chat, content=content, sender=Message.Sender.STUDENT)

    if faq is not None:
        msg.faq = faq

    msg.save()

    next_message = Message(chat=chat, content=None, sender=Message.Sender.ASSISTANT, state=Message.States.PENDING)
    if faq is not None:
        next_message.faq = faq
    next_message.save()

    background_tasks.add_task(ChatService.start_next_message, chat, next_message)

    return MessageResponse(
        message_id=msg.message_id,
        content=msg.content,
        sender=msg.sender,
        state=msg.state,
        created_at=str(msg.created_at),
        streaming=False,
        websocket=None,
        from_faq=msg.faq is not None,
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
    session: Session = Depends(get_current_session)
) -> MessagesResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = find_chat_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    access = False
    if course.canvas_id in session.admin_courses:
        log().warn(f"admin user {session.public_id} fetched chat details for chat {chat.public_id}")
        access = True

    if not access and chat.session.id != session.id:
        log().warn("user tried to get messages in chat thad didn't belong to the user")
    else:
        access = True

    if not access:
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

        feedback_id = None
        if msg.sender == Message.Sender.FEEDBACK:
            feedback = find_feedback_by_message_private_id(msg.id)
            if feedback is None:
                raise HTTPException(status_code=500, detail="failed to find feedback for feedback message")

            feedback_id = feedback.feedback_id
            if feedback.answer != QUESTION_UNANSWERED and feedback.answer is not None:
                content = feedback.answer

        out.append(MessageResponse(
            message_id=msg.message_id,
            content=content,
            sender=msg.sender,
            state=msg.state,
            created_at=str(msg.created_at),
            streaming=streaming,
            websocket=websocket,
            from_faq=msg.faq is not None,
            feedback_id=feedback_id
        ))

    return MessagesResponse(messages=out)


@router.get(
    '/course/{course_canvas_id}/chat/{chat_id}/messages/{message_id}',
    dependencies=[Depends(get_current_session)],
    status_code=status.HTTP_200_OK,
    response_model=MessageResponse
)
async def get_message(
    course_canvas_id: str,
    chat_id: str,
    message_id: str,
    session: Session = Depends(get_current_session)
) -> MessageResponse:
    course = find_course_by_canvas_id(course_canvas_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    chat = find_chat_by_id(chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    access = False
    if course.canvas_id in session.admin_courses:
        log().warn(f"admin user {session.public_id} fetched chat details for chat {chat.public_id}")
        access = True

    if not access and chat.session.id != session.id:
        log().warn("user tried to get message in chat thad didn't belong to the user")
    else:
        access = True

    if not access:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

    msg = find_message_by_chat_private_id_and_message_public_id(chat.id, message_id)
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

    feedback_id = None
    if msg.sender == Message.Sender.FEEDBACK:
        feedback = find_feedback_by_message_private_id(msg.id)
        if feedback is None:
            raise HTTPException(status_code=500, detail="failed to find feedback for feedback message")

        feedback_id = feedback.feedback_id
        if feedback.answer != QUESTION_UNANSWERED and feedback.answer is not None:
            content = feedback.answer

    return MessageResponse(
        message_id=msg.message_id,
        content=content,
        sender=msg.sender,
        state=msg.state,
        created_at=str(msg.created_at),
        streaming=streaming,
        websocket=websocket,
        feedback_id=feedback_id,
        from_faq=msg.faq is not None,
    )
