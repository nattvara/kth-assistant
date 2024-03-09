

def test_index_responds_with_hello(api_client):
    response = api_client.get('/')

    assert response.status_code == 200
    assert response.json() == {'message': 'hello there.'}
