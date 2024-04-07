from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from db.actions.feedback_question import get_all_active_feedback_questions, find_feedback_question_by_public_id
from db.actions.message import find_message_by_public_id
from db.models import Feedback
from http_api.auth import get_current_session

router = APIRouter()


class FeedbackQuestion(BaseModel):
    feedback_question_id: str
    question: str
    extra_data: dict


class FeedbackQuestionsResponse(BaseModel):
    questions: List[FeedbackQuestion]


class FeedbackResponse(BaseModel):
    language: str
    feedback_question_id: str
    message_id: str
    answer: str


class FeedbackRequestBody(BaseModel):
    choice: str


@router.get(
    '/feedback/{language}',
    dependencies=[Depends(get_current_session)],
    response_model=FeedbackQuestionsResponse
)
async def get_feedback_questions(language: str) -> FeedbackQuestionsResponse:
    if language not in ['en', 'sv']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported language")

    questions = get_all_active_feedback_questions()
    out = []
    for question in questions:
        out.append(question.to_dict_in_language(language))

    return FeedbackQuestionsResponse(
        questions=out
    )

@router.post(
    '/feedback/{language}/question/{feedback_question_id}/messages/{message_id}',
    dependencies=[Depends(get_current_session)],
    status_code=status.HTTP_201_CREATED,
    response_model=FeedbackResponse
)
async def save_feedback(
    language: str,
    feedback_question_id: str,
    message_id: str,
    body: FeedbackRequestBody
) -> FeedbackResponse:
    feedback_question = find_feedback_question_by_public_id(feedback_question_id)
    if feedback_question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback question not found")

    message = find_message_by_public_id(message_id)
    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message was not found")

    choice = body.choice

    feedback = Feedback(
        feedback_question=feedback_question,
        message=message,
        answer=choice,
        language=language
    )
    feedback.save()

    return FeedbackResponse(
        language=feedback.language,
        feedback_question_id=feedback.feedback_question.feedback_question_id,
        message_id=feedback.message.message_id,
        answer=feedback.answer,
    )
