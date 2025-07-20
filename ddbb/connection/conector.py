import mysql.connector
from config import Config

def get_mysql_connection():
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )

print("[DEBUG] MySQL Config:", Config.MYSQL_HOST, Config.MYSQL_USER, Config.MYSQL_PASSWORD, Config.MYSQL_DATABASE)
