import psycopg2
from psycopg2 import sql

def create_database(dbname, user, password, host='localhost', port='5432'):
    # Connect to the PostgreSQL server
    conn = psycopg2.connect(
        dbname='database',  # Connect to the default database to create a new one
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.autocommit = True  # Set autocommit to true so that the database creation is committed
    cursor = conn.cursor()
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
    cursor.close()
    conn.close()
    print(f"Database {dbname} created successfully.")

# Example usage
create_database(
    dbname='database',
    user='postgres',
    password='1123',
    port='5432'  # Specify the new port here
)
