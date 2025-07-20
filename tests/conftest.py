import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))





import pytest
from app import create_app
from app.extensions import db as sqlalchemy_db
from app.config import TestConfig



@pytest.fixture(scope="session")
def test_app():
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        yield app

@pytest.fixture(scope="function")
def client(test_app):
    with test_app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clean_database(test_app):
    """
    Limpia las tablas antes de cada test.
    """
    with test_app.app_context():
        sqlalchemy_db.drop_all()
        sqlalchemy_db.create_all()
        yield
        sqlalchemy_db.session.remove()
        sqlalchemy_db.drop_all()
