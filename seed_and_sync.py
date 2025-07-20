import mysql.connector
import uuid
from datetime import datetime
from ddbb.connection.conector import get_mysql_connection

from firebase.firebase_init import get_firebase_db



def seed_mysql(conn):
    cursor = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 1. Usuarios
    users = [
        ("admin01", "admin01@example.com", "hash1", "Admin Uno", "admin"),
        ("tutor_julia", "julia.tutor@example.com", "hash2", "Julia Tutor", "tutor"),
        ("alumno_mario", "mario.alumno@example.com", "hash3", "Mario Alumno", "alumno"),
        ("alumno_luisa", "luisa.alumno@example.com", "hash4", "Luisa Estudiante", "alumno")
    ]
    cursor.executemany("""
        INSERT IGNORE INTO users (username,email,password_hash,full_name,role,created_at,updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, [(u+ (now,now)) for u in users])

    # 2. Cursos (dos creados por tutor_julia id=2)
    courses = [
        ("Python Básico", "Fundamentos Python", 49.99, 20, 2, None, "publicado", now, now),
        ("JS Intermedio", "Profundiza en JavaScript", 59.99, 25, 2, None, "borrador", now, now)
    ]

    


    cursor.executemany("""
        INSERT IGNORE INTO courses
        (title,description,price,duration,tutor_id,admin_id,status,created_at,updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, courses)

    # 3. student_courses (Mario y Luisa en curso Python).
    sc = [
        (3, 1, "verificado", now, "url1", now),
        (4, 1, "pendiente", now, "url2", now)
    ]

    print("[DEBUG] student_courses data:", sc)

    cursor.executemany("""
        INSERT IGNORE INTO student_courses
        (student_id,course_id,payment_status,payment_date,payment_receipt_url,created_at)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, sc)

    # 4. Payments
    payments = [
        (3,1,49.99,"tarjeta","recibo1.png",True, now),
        (4,1,49.99,"paypal","recibo2.png",False, now)
    ]
    cursor.executemany("""
        INSERT IGNORE INTO payments
        (student_id,course_id,amount,payment_method,receipt_url,verified,created_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, payments)

    conn.commit()
    cursor.close()


def sync_to_firebase(conn):
    cursor = conn.cursor(dictionary=True)

    def clean_row(row):
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, datetime):
                cleaned[k] = v.isoformat()  # o el formato que prefieras
            else:
                cleaned[k] = v
        return cleaned

    def upload(path, rows):
        data = {str(r['id']): clean_row(r) for r in rows}
        get_firebase_db().reference(path).set(data)

    for tbl in ["users", "courses", "student_courses", "payments"]:
        cursor.execute(f"SELECT * FROM {tbl}")
        upload(tbl, cursor.fetchall())

    cursor.close()


def main():
    conn = get_mysql_connection()

    print("🌱 Sembrando datos de prueba en MySQL...")
    seed_mysql(conn)
    print("✅ Datos insertados en MySQL.")

    print("🔁 Sincronizando datos hacia Firebase...")
    sync_to_firebase(conn)
    print("✅ Sincronización completada.")

    conn.close()


if __name__ == "__main__":
    main()
