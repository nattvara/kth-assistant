

def test_health_endpoint_contains_db_state(api_client, mocker):
    mocker.patch('http_api.routers.health.test_redis', return_value='redis is working.')
    response = api_client.get('/health')
    data = response.json()

    assert response.status_code == 200
    assert 'database' in data
    assert data['database'] == 'db is working fine.'


def test_health_endpoint_contains_redis_state(api_client, mocker):
    mocker.patch('http_api.routers.health.test_redis', return_value='redis is working.')
    response = api_client.get('/health')
    data = response.json()

    assert response.status_code == 200
    assert 'redis' in data
    assert data['redis'] == 'redis is working.'
