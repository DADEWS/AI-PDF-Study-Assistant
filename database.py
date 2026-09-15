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


# Test database connection
if __name__ == "__main__":
    connection = get_db_connection()

    print("MySQL connected successfully")

    connection.close()