from db.models import Session


def test_user_can_be_granted_a_session_by_visiting_auth_url(api_client):
    response = api_client.post('/session')
    data = response.json()

    assert response.status_code == 200
    assert 'public_id' in data
    assert Session.select().filter(Session.public_id == data['public_id']).exists()


def test_protected_route_with_valid_session(api_client):
    valid_session = Session()
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
    response = api_client.post('/session')
    data = response.json()

    session = Session.select().filter(Session.public_id == data['public_id']).first()
    assert session.consent is False


def test_consent_can_be_given(api_client):
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
