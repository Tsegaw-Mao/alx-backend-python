import sqlite3
import functools

# Decorator to handle opening and closing DB connections
def with_db_connection(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            # Pass the connection to the decorated function
            result = func(conn, *args, **kwargs)
        finally:
            conn.close()
        return result
    return wrapper

@with_db_connection
def fetch_users(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# Test the function
if __name__ == "__main__":
    users = fetch_users(query="SELECT * FROM users")
    print(users)
