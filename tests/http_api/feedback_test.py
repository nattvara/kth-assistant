from db.models.feedback_question import FeedbackQuestion
from services.chat.chat_service import ChatService
from db.models import Faq, Feedback


def test_feedback_questions_can_be_returned(api_client, authenticated_session):
    question_1 = FeedbackQuestion(
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'choices': ['yes', 'no']},
        extra_data_sv={'choices': ['ja', 'nej']},
    )
    question_2 = FeedbackQuestion(
        question_en="fast?",
        question_sv="snabb?",
        extra_data_en={'choices': ['very fast', 'slugish']},
        extra_data_sv={'choices': ['skit snabb', 'tok sakta']},
    )
    question_1.save()
    question_2.save()

    response = api_client.get('/feedback/en', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json() == {'questions': [
        {'feedback_question_id': question_1.feedback_question_id, 'question': "Good?", 'extra_data': {'choices': ['yes', 'no']}},  # noqa
        {'feedback_question_id': question_2.feedback_question_id, 'question': "fast?", 'extra_data': {'choices': ['very fast', 'slugish']}}  # noqa
    ]}

    response = api_client.get('/feedback/sv', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json() == {'questions': [
        {'feedback_question_id': question_1.feedback_question_id, 'question': "Bra?", 'extra_data': {'choices': ['ja', 'nej']}},  # noqa
        {'feedback_question_id': question_2.feedback_question_id, 'question': "snabb?", 'extra_data': {'choices': ['skit snabb', 'tok sakta']}}  # noqa
    ]}


def test_user_can_submit_feedback_for_message(api_client, authenticated_session, new_chat):
    question_1 = FeedbackQuestion(
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'choices': ['yes', 'no']},
        extra_data_sv={'choices': ['ja', 'nej']},
    )
    question_1.save()

    snapshot = ChatService.create_faq_snapshot(new_chat.course)
    faq_1 = Faq(question="And Why Do We Fall, Bruce?", snapshot=snapshot)
    faq_1.save()

    # submit first message from a faq
    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    api_client.post(url, json={'faq_id': faq_1.faq_id}, headers=authenticated_session.headers)
    new_chat.chat.refresh()

    # submit feedback response
    url = f'/feedback/sv/questions/{question_1.feedback_question_id}/messages/{new_chat.chat.messages[1].message_id}'
    response = api_client.post(url, json={'choice': 'yes'}, headers=authenticated_session.headers)

    assert response.status_code == 201
    assert Feedback.select().filter(
        Feedback.feedback_question == question_1
    ).filter(
        Feedback.message == new_chat.chat.messages[1]
    ).exists()


def test_user_can_check_if_question_has_been_answered(api_client, authenticated_session, new_chat):
    question_1 = FeedbackQuestion(
        question_en="Good?",
        question_sv="Bra?",
        extra_data_en={'choices': ['yes', 'no']},
        extra_data_sv={'choices': ['ja', 'nej']},
    )
    question_1.save()

    snapshot = ChatService.create_faq_snapshot(new_chat.course)
    faq_1 = Faq(question="And Why Do We Fall, Bruce?", snapshot=snapshot)
    faq_1.save()

    # submit first message from a faq
    url = f'/course/{new_chat.course.canvas_id}/chat/{new_chat.chat.public_id}/messages'
    api_client.post(url, json={'faq_id': faq_1.faq_id}, headers=authenticated_session.headers)
    new_chat.chat.refresh()

    # Answer shouldn't exist
    url = f'/feedback/sv/questions/{question_1.feedback_question_id}/messages/{new_chat.chat.messages[1].message_id}'
    response = api_client.get(url, headers=authenticated_session.headers)
    assert response.status_code == 404

    url = f'/feedback/sv/questions/{question_1.feedback_question_id}/messages/{new_chat.chat.messages[1].message_id}'
    response = api_client.post(url, json={'choice': 'yes'}, headers=authenticated_session.headers)
    assert response.status_code == 201

    # should now exist
    url = f'/feedback/sv/questions/{question_1.feedback_question_id}/messages/{new_chat.chat.messages[1].message_id}'
    response = api_client.get(url, headers=authenticated_session.headers)
    assert response.status_code == 200
