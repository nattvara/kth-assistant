from db.models.feedback_question import FeedbackQuestion


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

    response = api_client.get(f'/feedback/en', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json() == {'questions': [
        {'feedback_question_id': question_1.feedback_question_id, 'question': "Good?", 'extra_data': {'choices': ['yes', 'no']}},  # noqa
        {'feedback_question_id': question_2.feedback_question_id, 'question': "fast?", 'extra_data': {'choices': ['very fast', 'slugish']}}  # noqa
    ]}

    response = api_client.get(f'/feedback/sv', headers=authenticated_session.headers)

    assert response.status_code == 200
    assert response.json() == {'questions': [
        {'feedback_question_id': question_1.feedback_question_id, 'question': "Bra?", 'extra_data': {'choices': ['ja', 'nej']}},  # noqa
        {'feedback_question_id': question_2.feedback_question_id, 'question': "snabb?", 'extra_data': {'choices': ['skit snabb', 'tok sakta']}}  # noqa
    ]}
