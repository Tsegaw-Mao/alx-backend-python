import sqlite3  # Or use another DB connector like mysql.connector or psycopg2

def stream_users():
    conn = sqlite3.connect('your_database.db')  # Replace with your DB
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM user_data")

    for row in cursor:
        yield row  # Yields one row at a time

    cursor.close()
    conn.close()
for user in stream_users():
    print(user)
