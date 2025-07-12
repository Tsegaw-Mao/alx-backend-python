import sqlite3

class ExecuteQuery:
    def __init__(self, query, params=None):
        self.query = query
        self.params = params or []
        self.conn = None
        self.result = None

    def __enter__(self):
        self.conn = sqlite3.connect('users.db')
        cursor = self.conn.cursor()
        cursor.execute(self.query, self.params)
        self.result = cursor.fetchall()
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

# Usage example
if __name__ == "__main__":
    query = "SELECT * FROM users WHERE age > ?"
    param = [25]

    with ExecuteQuery(query, param) as results:
        print(results)
