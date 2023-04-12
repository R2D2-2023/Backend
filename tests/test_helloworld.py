import pytest
import json
from pathlib import Path
import sys
import psycopg2
from datetime import datetime, timedelta
from random import randint
from flask import url_for

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

@pytest.fixture()
def database():
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres'")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS sensor_data")
    cur.execute("CREATE TABLE sensor_data (datetime TIMESTAMP PRIMARY KEY, temperature INTEGER, co2 INTEGER, humidity INTEGER, pressure INTEGER, location INTEGER)")
    conn.commit()
    for i in range(100, 0, -1):
        cur.execute(f"INSERT INTO sensor_data (datetime, temperature, co2, humidity, pressure, location) VALUES ('{datetime.now() - timedelta(minutes=i)}', {randint(10,30)}, {randint(400, 1000)}, {randint(20,100)}, {randint(800,1300)}, 1)")
    conn.commit()

def test_verify_testing(app):
    assert app.config['TESTING'] == True

def test_request_example(client):
    response = client.get("/does_not_exist")
    assert response.status_code == 404

def test_get_new_data_expect_empty(client, database):
    data = {
    'last_datapoint': f'{datetime.now().isoformat()}',
    'location': '1'}
    response = client.get("/get_new_data", query_string=data)
    assert response.status_code == 200
    assert b"No new data available." in response.data
    assert b"Not the right parameters are given." not in response.data

def test_get_new_data_expect_wrong_parameters(client, database):
    data = {
    'last_datapoint': f'{(datetime.now() - timedelta(minutes=50)).isoformat()}'
    }
    response = client.get("/get_new_data", query_string=data)
    assert response.status_code == 200
    assert b"No new data available." not in response.data
    assert b"Not the right parameters are given." in response.data

def test_get_new_data_expect_data(client, database):
    data = {
    'last_datapoint': f'{(datetime.now() - timedelta(minutes=50)).isoformat()}',
    'location': '1'}
    response = client.get("/get_new_data", query_string=data)
    assert response.status_code == 200
    assert b"No new data available." not in response.data
    assert b"Not the right parameters are given." not in response.data
    

def test_get_new_data_only_get_newer_data(client, database):
    data = {
    'last_datapoint': f'{(datetime.now() - timedelta(minutes=10)).isoformat()}',
    'location': '1'}
    response = client.get("/get_new_data", query_string=data)
    assert response.status_code == 200
    assert b"No new data available." not in response.data
    assert b"Not the right parameters are given." not in response.data
    json_data = json.loads(response.data)
    assert len(json_data["timestamp"])
    
# def test_utility_processor(client):
#     response = client.get("/utility_processor")
#     assert response.status_code == 200
#     assert b"Utility processor is running" in response.data



