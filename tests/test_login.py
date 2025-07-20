from app.extensions import db



def test_login_success(client):
    response = client.post('/auth/login', data={
        'username': 'testuser123',
        'password': 'TestPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Bienvenido' in response.get_data(as_text=True) or 'Dashboard' in response.get_data(as_text=True) or 'Sesión iniciada' in response.get_data(as_text=True)



def test_login(client):
    client.post('/register', data={
        'username': 'testlogin',
        'email': 'testlogin@example.com',
        'password': '123456',
        'confirm': '123456',
        'full_name': 'Login User',
        'role': 'alumno'
    })
    response = client.post('/login', data={
        'username': 'testlogin',
        'password': '123456'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Bienvenido' in response.get_data(as_text=True) or 'Dashboard' in response.get_data(as_text=True) or 'Sesión iniciada' in response.get_data(as_text=True)



def test_login_user(test_client):
    # Primero registrar
    test_client.post('/register', data={
        'username': 'testlogin',
        'email': 'login@example.com',
        'password': 'test123',
        'confirm_password': 'test123'
    }, follow_redirects=True)

    # Ahora login
    response = test_client.post('/login', data={
        'email': 'login@example.com',
        'password': 'test123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert 'Bienvenido' in response.get_data(as_text=True) or 'Dashboard' in response.get_data(as_text=True) or 'Sesión iniciada' in response.get_data(as_text=True)

