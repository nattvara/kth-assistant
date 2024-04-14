from services.index.supported_indices import IndexType
from services.llm.supported_models import LLMModel
from db.models import Session, ChatConfig


def test_user_can_be_granted_a_session_by_visiting_auth_url(api_client):
    config = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config.save()

    response = api_client.post('/session')
    data = response.json()

    assert response.status_code == 200
    assert 'public_id' in data
    assert Session.select().filter(Session.public_id == data['public_id']).exists()


def test_protected_route_with_valid_session(api_client):
    valid_session = Session(default_llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, default_index_type=IndexType.NO_INDEX)
    valid_session.save()

    headers = {'X-Session-ID': valid_session.public_id, 'Content-Type': 'application/json'}
    response = api_client.get('/session/me', headers=headers)
    data = response.json()

    assert response.status_code == 200
    assert valid_session.public_id in data['message']


def test_protected_route_with_invalid_session(api_client):
    headers = {'X-Session-ID': 'something-invalid', 'Content-Type': 'application/json'}
    response = api_client.get('/session/me', headers=headers)

    assert response.status_code == 401


def test_consent_is_not_given_by_default(api_client):
    config = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config.save()

    response = api_client.post('/session')
    data = response.json()

    session = Session.select().filter(Session.public_id == data['public_id']).first()
    assert session.consent is False


def test_consent_can_be_given(api_client):
    config = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config.save()

    response = api_client.post('/session')
    session = Session.select().filter(Session.public_id == response.json()['public_id']).first()

    headers = {'X-Session-ID': response.json()['public_id'], 'Content-Type': 'application/json'}
    response = api_client.post('/session/consent', json={'granted': True}, headers=headers)

    session.refresh()
    assert response.status_code == 200
    assert session.consent is True


def test_consent_can_be_checked(api_client, authenticated_session):
    response = api_client.get('/session/me', headers=authenticated_session.headers)
    data = response.json()

    assert data['consent'] is True


def test_user_is_assigned_a_default_llm_model_and_index_type_when_session_is_started(mocker, api_client):
    config_1 = ChatConfig(llm_model_name=LLMModel.MISTRAL_7B_INSTRUCT, index_type=IndexType.NO_INDEX)
    config_2 = ChatConfig(llm_model_name=LLMModel.OPENAI_GPT4, index_type=IndexType.NO_INDEX)
    config_1.save()
    config_2.save()
    mocker.patch(
        'db.actions.chat_config.get_random_chat_config',
        side_effect=[config_1, config_2]
    )

    response = api_client.post('/session')
    session = Session.select().filter(Session.public_id == response.json()['public_id']).first()
    assert config_1.llm_model_name == session.default_llm_model_name
    assert config_1.index_type == session.default_index_type

    response = api_client.post('/session')
    session = Session.select().filter(Session.public_id == response.json()['public_id']).first()
    assert config_2.llm_model_name == session.default_llm_model_name
    assert config_2.index_type == session.default_index_type
