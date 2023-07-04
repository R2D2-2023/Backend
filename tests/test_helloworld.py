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
from models import config_db
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
    cur.execute("DROP TABLE IF EXISTS sensor_data_with_foreign_location")
    cur.execute("DROP TABLE IF EXISTS locatie_only")
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS emailaddress")
    cur.execute("CREATE TABLE locatie_only (datetime TIMESTAMP WITHOUT TIME ZONE PRIMARY KEY, x_loc INTEGER, y_loc INTEGER)")
    cur.execute("CREATE TABLE sensor_data_with_foreign_location (datetime TIMESTAMP WITHOUT TIME ZONE PRIMARY KEY, temperature numeric(3,1), co2 INTEGER, humidity INTEGER, pressure INTEGER, pm10 integer, pm25 integer, pm100 integer, zone INTEGER, FOREIGN KEY (datetime) REFERENCES locatie_only (datetime) )")
    cur.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR(100) UNIQUE, email VARCHAR(100) UNIQUE, password_hash TEXT)")
    cur.execute("CREATE TABLE emailaddress (adress VARCHAR(100) PRIMARY KEY)")
    conn.commit()
    for i in range(100, 0, -1):
        datetime_now = datetime.now() - timedelta(minutes=i)
        cur.execute(f"INSERT INTO locatie_only (datetime, x_loc, y_loc) VALUES ('{datetime_now}', {randint(0,232)}, {randint(0,65)})")
        cur.execute(f"INSERT INTO sensor_data_with_foreign_location (datetime, temperature, co2, humidity, pressure, pm10, pm25, pm100, zone) VALUES ('{datetime_now}', {randint(20, 30)}, {randint(400,1000)}, {randint(40,60)}, {randint(1000,1100)}, {randint(0,100)}, {randint(0,100)}, {randint(0,100)}, {1})")
    conn.commit()

@pytest.fixture()
def login(client, database):
    response = client.get("/register")
    assert response.status_code == 200
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/register", data=dict(email="test@test.nl", password="test", username="test", csrf_token=csrf_token), follow_redirects=True)
    assert response.status_code == 200
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/login", data=dict(email="test@test.nl", password="test", csrf_token=csrf_token), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>M3-S Dashboard</title>" in response.data

def test_verify_testing(app):
    assert app.config['TESTING'] == True

def test_request_example(client):
    response = client.get("/does_not_exist")
    assert response.status_code == 404

def test_get_new_data_expect_empty(client, database):
    data = {
    'last_datapoint': f'{datetime.now().isoformat()}',
    'first_datapoint': f'{(datetime.now()).isoformat()}',
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
    'first_datapoint': f'{(datetime.now()).isoformat()}',
    'location': '1'}
    response = client.get("/get_new_data", query_string=data)
    assert response.status_code == 200
    assert b"No new data available." not in response.data
    assert b"Not the right parameters are given." not in response.data
    

def test_get_new_data_only_get_newer_data(client, database):
    data = {
    'last_datapoint': f'{(datetime.now() - timedelta(minutes=10)).isoformat()}',
    'first_datapoint': f'{(datetime.now()).isoformat()}',
    'location': '1023'}
    response = client.get("/get_new_data", query_string=data)
    assert response.status_code == 200
    assert b"No new data available." not in response.data
    assert b"Not the right parameters are given." not in response.data
    json_data = json.loads(response.data)
    assert len(json_data["timestamp"])

def test_login_client(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_not_logged_in(client, database):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login(client, database, login):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>M3-S Dashboard</title>" in response.data

def test_logout(client, database, login):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_email_register(client, database, login):
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test@test.com", csrf_token=csrf_token), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Email</title>" in response.data

def test_email_register_already_exists(client, database, login):
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test@test.com", csrf_token=csrf_token, submit="true"), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Email</title>" in response.data
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test@test.com", csrf_token=csrf_token, submit="true"), follow_redirects=True)    
    print(response.data)
    assert response.status_code == 200
    assert b"Your e-mail is already in our database" in response.data

def test_email_remove(client, database, login):
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test@test.com", csrf_token=csrf_token, submit="true"), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Email</title>" in response.data
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test@test.com", csrf_token=csrf_token, remove="test"), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Email</title>" in response.data
    assert b"The given e-mail has been removed from our database" in response.data
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test@test.com", csrf_token=csrf_token, remove="test"), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Email</title>" in response.data
    assert b"Mail adress not found in our database" in response.data

def test_email_invalid_email(client, database, login):
    response = client.get("/email")
    assert response.status_code == 200
    assert b"Email" in response.data
    csrf_token = response.data.decode("utf-8").split("csrf_token")[1].split("value=\"")[1].split("\"")[0]
    response = client.post("/email", data=dict(email="test", csrf_token=csrf_token, submit="true"), follow_redirects=True)
    assert response.status_code == 200
    assert b"<title>Email</title>" in response.data
    assert b"Not a valid mail adress" in response.data

    

    
