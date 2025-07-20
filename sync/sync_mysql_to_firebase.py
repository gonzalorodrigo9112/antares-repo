from conector import get_mysql_connection
from firebase_init import get_firebase_db


def upload_to_firebase(path, data):
    """Sube un diccionario de datos a Firebase en la ruta especificada."""
    db_ref = get_firebase_db().reference(path)
    db_ref.set(data)


def main():
    # Conexión a MySQL
    conn = get_mysql_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # 1. Users
        cursor.execute("SELECT * FROM users LIMIT 3")
        users = cursor.fetchall()
        users_dict = {str(user['id']): user for user in users}
        upload_to_firebase("users", users_dict)

        # 2. Courses
        cursor.execute("SELECT * FROM courses LIMIT 3")
        courses = cursor.fetchall()
        courses_dict = {str(course['id']): course for course in courses}
        upload_to_firebase("courses", courses_dict)

        # 3. Student-Course Relationships
        cursor.execute("SELECT * FROM student_courses LIMIT 3")
        student_courses = cursor.fetchall()
        student_courses_dict = {str(sc['id']): sc for sc in student_courses}
        upload_to_firebase("student_courses", student_courses_dict)

        # 4. Payments
        cursor.execute("SELECT * FROM payments LIMIT 3")
        payments = cursor.fetchall()
        payments_dict = {str(pay['id']): pay for pay in payments}
        upload_to_firebase("payments", payments_dict)

        print("✅ Datos subidos correctamente a Firebase Realtime Database.")

    except Exception as e:
        print(f"❌ Error durante la sincronización: {e}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
