from db.models.feedback import QUESTION_UNANSWERED
from db.models.feedback_question import FeedbackQuestion
from db.models import Feedback, Message, Course


def test_feedback_question_can_be_returned_from_feedback_id(api_client, authenticated_session, new_chat):
    question_1 = FeedbackQuestion(
        trigger="chat:2:message:4",
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'choices': ['yes', 'no']},
        extra_data_sv={'choices': ['ja', 'nej']},
    )
    question_1.save()
    message = Message(chat=new_chat.chat, content=None, sender=Message.Sender.ASSISTANT)
    message.save()
    feedback = Feedback(
        feedback_question=question_1,
        message=message,
        answer=QUESTION_UNANSWERED,
        language=Course.Language.ENGLISH,
    )
    feedback.save()

    response = api_client.get(f'/feedback/{feedback.feedback_id}', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json() == {'feedback_question_id': question_1.feedback_question_id, 'question': "Good?", 'extra_data': {'choices': ['yes', 'no']}}  # noqa

    feedback.language = Course.Language.SWEDISH
    feedback.save()
    response = api_client.get(f'/feedback/{feedback.feedback_id}', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json() == {'feedback_question_id': question_1.feedback_question_id, 'question': "Bra?", 'extra_data': {'choices': ['ja', 'nej']}}  # noqa


def test_user_can_submit_feedback_for_message(api_client, authenticated_session, new_chat):
    question_1 = FeedbackQuestion(
        trigger="chat:2:message:4",
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'choices': ['yes', 'no']},
        extra_data_sv={'choices': ['ja', 'nej']},
    )
    question_1.save()
    message = Message(chat=new_chat.chat, content=None, sender=Message.Sender.ASSISTANT)
    message.save()
    feedback = Feedback(
        feedback_question=question_1,
        message=message,
        answer=QUESTION_UNANSWERED,
        language=Course.Language.ENGLISH,
    )
    feedback.save()

    response = api_client.post(
        f'/feedback/{feedback.feedback_id}',
        json={'choice': 'yes'},
        headers=authenticated_session.headers,
    )
    feedback.refresh()

    assert response.status_code == 200
    assert feedback.answer == 'yes'
