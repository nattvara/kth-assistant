from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from db.actions.feedback import find_feedback_by_public_id
from http_api.auth import get_current_session

router = APIRouter()


class FeedbackQuestionResponse(BaseModel):
    feedback_question_id: str
    question: str
    extra_data: dict


class FeedbackResponse(BaseModel):
    answer: str


class FeedbackRequestBody(BaseModel):
    choice: str


@router.get(
    '/feedback/{feedback_id}',
    dependencies=[Depends(get_current_session)],
    response_model=FeedbackQuestionResponse
)
async def get_feedback_questions(feedback_id: str) -> FeedbackQuestionResponse:
    feedback = find_feedback_by_public_id(feedback_id)
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    q = feedback.feedback_question.to_dict_in_language(feedback.language)
    return FeedbackQuestionResponse(
        feedback_question_id=q['feedback_question_id'],
        question=q['question'],
        extra_data=q['extra_data'],
    )


@router.post(
    '/feedback/{feedback_id}',
    dependencies=[Depends(get_current_session)],
    status_code=status.HTTP_200_OK,
    response_model=FeedbackResponse
)
async def save_feedback(
    feedback_id: str,
    body: FeedbackRequestBody
) -> FeedbackResponse:
    feedback = find_feedback_by_public_id(feedback_id)
    if feedback is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found")

    choice = body.choice

    feedback.answer = choice
    feedback.save()

    return FeedbackResponse(answer=feedback.answer)
