
def get_all_active_feedback_questions():
    from db.models.feedback_question import FeedbackQuestion
    return FeedbackQuestion.select().where(FeedbackQuestion.is_active == True)  # noqa


def find_feedback_question_by_public_id(feedback_question_id: str):
    from db.models.feedback_question import FeedbackQuestion
    return FeedbackQuestion.select().filter(FeedbackQuestion.feedback_question_id == feedback_question_id).first()
