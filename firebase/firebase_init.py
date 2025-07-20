import os
import firebase_admin
from firebase_admin import credentials, db
from dotenv import load_dotenv

load_dotenv()

cred_path = os.getenv("FIREBASE_CRED_PATH")
if not cred_path:
    cred_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "firebase", "clave_privada.json"
    )

db_url = os.getenv("FIREBASE_DB_URL")

print(f"[DEBUG] cred_path: {cred_path}")
print(f"[DEBUG] db_url: {db_url}")

if not os.path.isfile(cred_path):
    raise FileNotFoundError(f"No se encontró la clave privada: {cred_path}")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': db_url
    })

def get_firebase_db():
    return db
