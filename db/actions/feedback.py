
def find_feedback_by_private_feedback_question_id_and_message_id(feedback_question_id: int, message_id: int):
    from db.models.feedback import Feedback
    return Feedback.select().filter(
        Feedback.feedback_question == feedback_question_id
    ).filter(
        Feedback.message == message_id
    ).first()


def find_feedback_by_message_private_id(message_id: int):
    from db.models.feedback import Feedback
    return Feedback.select().filter(
        Feedback.message_id == message_id
    ).first()


def find_feedback_by_public_id(feedback_id: str):
    from db.models.feedback import Feedback
    return Feedback.select().filter(
        Feedback.feedback_id == feedback_id
    ).first()
