"""
I haven't time and tests are run not from the first time because data haven't
time to sync between all nodes
"""
from app.main import create_app


async def test_update(test_client):
    """
    tests for "update" view
    :return: 200
    """
    client = await test_client(create_app)

    resp = await client.post('/update')
    assert resp.status == 400

    resp = await client.post('/update', json={})
    assert resp.status == 400

    data = {'wrong_key': 'wrong_value'}
    resp = await client.post('/update', json=data)
    assert resp.status == 400

    data = {
        'name': 'test_marketing',
        'author': 'John Smith',
        'timestamp': 20140812003842
    }
    resp = await client.post('/update', json=data)
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {
        'test_marketing': {
            'author': 'John Smith', 'timestamp': 20140812003842
        }
    }


async def test_get(test_client):
    """
    tests for "get" view
    :return: 200
    """
    client = await test_client(create_app)

    resp = await client.get('/get')
    assert resp.status == 400

    resp = await client.get('/get?wrong_key=wrong_value')
    assert resp.status == 400

    resp = await client.get('/get?name=test_marketing')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == {'timestamp': 20140812003842, 'author': 'John Smith'}


async def test_dump(test_client):
    """
    tests for "dump" view
    :return: 200
    """
    client = await test_client(create_app)

    resp = await client.get('/dump')
    assert resp.status == 200
    resp_json = await resp.json()
    assert 'test_marketing' in resp_json.keys()


async def test_get_history(test_client):
    """
    tests for "get_history" view
    :return: 200
    """
    client = await test_client(create_app)

    data = {
        'name': 'test_marketing',
        'author': 'John Smith',
        'timestamp': 20150812003842
    }
    await client.post('/update', json=data)

    resp = await client.get('/getHistory')
    assert resp.status == 400

    resp = await client.get('/getHistory?wrong_key=wrong_value')
    assert resp.status == 400

    resp = await client.get('/getHistory?name=test_marketing')
    assert resp.status == 200
    resp_json = await resp.json()
    assert resp_json == [
        {'timestamp': 20150812003842, 'author': 'John Smith'},
        {'timestamp': 20140812003842, 'author': 'John Smith'}
    ]


async def test_remove(test_client):
    """
    tests for "remove" view
    :return: 204
    """
    client = await test_client(create_app)

    resp = await client.get('/remove')
    assert resp.status == 400

    resp = await client.get('/remove?wrong_key=wrong_value')
    assert resp.status == 400

    resp = await client.get('/remove?name=test_marketing')
    assert resp.status == 204
