#!/usr/bin/python3

import seed

def stream_users_in_batches(batch_size):
    """
    Generator that yields user rows in batches from the user_data table.
    Each batch is a list of rows, where each row is a tuple.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, name, email, age FROM user_data;")

    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """
    Processes batches of users, filtering those over age 25.
    Prints them.
    """
    for batch in stream_users_in_batches(batch_size):
        filtered = [user for user in batch if float(user[3]) > 25]  # age is at index 3
        for user in filtered:
            print(user)


if __name__ == "__main__":
    batch_processing(10)
