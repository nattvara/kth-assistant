
def get_all_active_feedback_questions():
    from db.models.feedback_question import FeedbackQuestion
    return FeedbackQuestion.select().where(FeedbackQuestion.is_active == True)  # noqa
