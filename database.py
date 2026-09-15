# Import operating system tools
import os

# Import MySQL connector
import mysql.connector

# Import environment tools
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Create a MySQL database connection
def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return connection

# Create a new user
def create_user(username, email, password_hash):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (username, email, password_hash)
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return user_id


# Find a user by username or email
def get_user_by_login(login):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT id, username, email, password_hash
        FROM users
        WHERE username = %s OR email = %s
        LIMIT 1
    """

    cursor.execute(
        query,
        (login, login)
    )

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


# Test database connection
if __name__ == "__main__":
    connection = get_db_connection()

    print("MySQL connected successfully")

    connection.close()