import csv
import uuid
import mysql.connector

CSV_FILE = 'user_data.csv'

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",
        password="your_mysql_password"
    )

def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    connection.commit()
    cursor.close()

def connect_to_prodev():
    return mysql.connector.connect(
        host="localhost",
        user="your_mysql_username",
        password="your_mysql_password",
        database="ALX_prodev"
    )

def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX(user_id)
        )
    """)
    connection.commit()
    cursor.close()

def insert_data(connection, data):
    cursor = connection.cursor()
    for row in data:
        name, email, age = row
        user_id = str(uuid.uuid4())
        cursor.execute("""
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (%s, %s, %s, %s)
        """, (user_id, name, email, age))
    connection.commit()
    cursor.close()

def read_csv(file_path):
    with open('./user_data.csv', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        return list(reader)

if __name__ == "__main__":
    root_conn = connect_db()
    create_database(root_conn)
    root_conn.close()

    db_conn = connect_to_prodev()
    create_table(db_conn)
    data = read_csv(CSV_FILE)
    insert_data(db_conn, data)
    db_conn.close()
