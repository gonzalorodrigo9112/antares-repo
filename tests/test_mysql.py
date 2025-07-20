# test_mysql.py
from ddbb.connection.conector import get_mysql_connection

from app.extensions import db


conn = get_mysql_connection()
cursor = conn.cursor()
cursor.execute("SHOW TABLES;")
print(cursor.fetchall())
conn.close()
