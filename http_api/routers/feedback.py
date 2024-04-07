from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from starlette import status

from db.actions.feedback_question import get_all_active_feedback_questions
from http_api.auth import get_current_session

router = APIRouter()


class FeedbackQuestion(BaseModel):
    feedback_question_id: str
    question: str
    extra_data: dict


class FeedbackQuestionsResponse(BaseModel):
    questions: List[FeedbackQuestion]


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
