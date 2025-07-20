import pytest
from flask import Flask

from app.extensions import db



@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Si usás Flask-WTF
    with flask_app.test_client() as client:
        yield client

def test_register_success(client):
    response = client.post('/auth/register', data={
        'username': 'testuser123',
        'full_name': 'Test User',
        'email': 'testuser123@example.com',
        'password': 'TestPassword123',
        'rol': 'alumno'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Inicio de sesión' in response.get_data(as_text=True)



def test_register(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': '123456',
        'confirm': '123456',
        'full_name': 'Test User',
        'role': 'alumno'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Inicio de sesión' in response.get_data(as_text=True)




def test_register_user(test_client):
    response = test_client.post('/register', data={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': '123456',
        'confirm_password': '123456'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Inicio de sesión' in response.get_data(as_text=True)

