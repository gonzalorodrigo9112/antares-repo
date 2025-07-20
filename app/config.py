# app/config.py

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/test_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    FIREBASE_DB_URL = 'https://<tu-url>.firebaseio.com/'
    FIREBASE_CREDENTIALS = 'firebase/clave_privada_test.json'
