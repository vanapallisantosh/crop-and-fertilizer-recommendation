import mysql.connector

def test_connection():
    print("🔄 Attempting to connect to MySQL (without database)...")

    try:
        print("🔍 Creating connection object...")
        conn = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="Santosh@366",
        port=3306,
        connection_timeout=5,
        use_pure=True  # Force pure Python mode
)

        print("✅ Connected to MySQL! (But no database selected)")
        conn.close()

    except mysql.connector.Error as err:
        print("❌ ERROR: Unable to connect to MySQL.")
        print(f"🔴 Detailed Error: {err}")

test_connection()
