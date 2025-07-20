from firebase_admin import db as firebase_db

def test_firebase_connection():
    ref = firebase_db.reference("test_connection")
    ref.set({"message": "Hola Firebase"})
    assert ref.get() == {"message": "Hola Firebase"}