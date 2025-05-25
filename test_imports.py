import psycopg2

def test_connection():
    try:
        conn = psycopg2.connect(
            dbname="done_talking",
            user="hossam",
            password="hossam1442001",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        print(cursor.fetchone()[0])
        conn.close()
        print("✓ Raw psycopg2 connection works")
    except Exception as e:
        print(f"✗ Raw connection failed: {e}")

test_connection()