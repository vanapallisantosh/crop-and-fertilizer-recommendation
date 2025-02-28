import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        print("🔄 Trying to connect to MySQL...")  # Debugging message
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Santosh@366",
            database="flask_db"
        )
        if conn.is_connected():
            print("✅ Database connected successfully!")
            return conn
    except Error as e:
        print(f"❌ Database connection failed! Error: {e}")  # Show exact error
        return None
