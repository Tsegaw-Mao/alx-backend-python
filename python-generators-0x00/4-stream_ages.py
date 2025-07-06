#!/usr/bin/python3

import seed

def stream_user_ages():
    """
    Generator that yields user ages one at a time from the database.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor()
    cursor.execute("SELECT age FROM user_data;")
    
    for (age,) in cursor:
        yield float(age)  # Convert DECIMAL to float for averaging

    cursor.close()
    connection.close()


def calculate_average_age():
    """
    Calculates and prints the average age using the generator.
    """
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        print("No users found.")
    else:
        average = total_age / count
        print(f"Average age of users: {average:.2f}")


if __name__ == "__main__":
    calculate_average_age()
