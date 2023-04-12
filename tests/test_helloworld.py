import pytest
import json
from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))
print(sys.path)

from app import create_app
from models import config_db, SensorData
from routes import config_route

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

def test_helloworld(app):
    assert app.config['TESTING'] == True

def test_request_example(client):
    response = client.get("/posts")
    assert b"<h2>Hello, World!</h2>" in response.data
    assert response.status_code == 200

def test_write_to_db(client):
    response = client.get("/make_test_data")
    assert response.status_code == 200
    assert b"Test data created" in response.data


# def test_write_to_db(client):
#     response = client.post(
#         '/users',
#         data=json.dumps(dict(
#             username='michael',
#             email='michael@realpython.com'
#         )),
#         content_type='application/json',
#     )
#     data = json.loads(response.data.decode())
#     assert response.status_code == 201
#     assert 'michael@realpython.com was added!' in data['message']
#     assert 'success' in data['status']


