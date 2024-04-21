from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db.actions.course import find_course_by_canvas_id
from http_api.auth import get_current_session
from config.logger import log
from db.models import Session

router = APIRouter()


class Course(BaseModel):
    canvas_id: str
    language: str
    name: str


class CourseResponse(BaseModel):
    courses: List[Course]


@router.get(
    '/admin/courses',
    dependencies=[Depends(get_current_session)],
    response_model=CourseResponse
)
async def get_courses_user_can_administrate(session: Session = Depends(get_current_session)) -> CourseResponse:
    courses = []
    for canvas_id in session.admin_courses:
        course = find_course_by_canvas_id(canvas_id)
        if course is None:
            log().warning(f"found course id that doesn't exist: {canvas_id}, in session: {session.public_id}")
            continue
        courses.append(Course(
            canvas_id=course.canvas_id,
            language=course.language,
            name=course.name
        ))
    return CourseResponse(courses=courses)
