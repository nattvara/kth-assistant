

def test_health_endpoint_contains_db_state(api_client, mocker):
    mocker.patch('http_api.routers.health.test_redis', return_value='redis is working.')
    mocker.patch('services.index.opensearch.get_client')
    mocker.patch('services.index.opensearch.health_check')
    response = api_client.get('/health')
    data = response.json()

    assert response.status_code == 200
    assert 'database' in data
    assert data['database'] == 'db is working fine.'


def test_health_endpoint_contains_redis_state(api_client, mocker):
    mocker.patch('http_api.routers.health.test_redis', return_value='redis is working.')
    mocker.patch('services.index.opensearch.get_client')
    mocker.patch('services.index.opensearch.health_check')
    response = api_client.get('/health')
    data = response.json()

    assert response.status_code == 200
    assert 'redis' in data
    assert data['redis'] == 'redis is working.'


def test_health_endpoint_can_handle_database_unavailable(api_client, mocker):
    mocker.patch('http_api.routers.health.test_db', side_effect=ValueError)
    mocker.patch('services.index.opensearch.get_client')
    mocker.patch('services.index.opensearch.health_check')
    response = api_client.get('/health')
    data = response.json()

    assert response.status_code == 503
    assert 'database' in data
    assert data['database'] == 'db is NOT working.'


def test_health_endpoint_can_handle_redis_unavailable(api_client, mocker):
    mocker.patch('http_api.routers.health.test_redis', side_effect=ValueError)
    mocker.patch('services.index.opensearch.get_client')
    mocker.patch('services.index.opensearch.health_check')
    response = api_client.get('/health')
    data = response.json()

    assert response.status_code == 503
    assert 'redis' in data
    assert data['redis'] == 'redis is NOT working.'
