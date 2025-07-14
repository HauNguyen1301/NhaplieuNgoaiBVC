import sqlite3
import os

DB_FILE = "database/boithuong.db"
SCHEMA_FILE = "database/schema.sql"
DATA_FILE = "database/data.sql"

def create_database():
    # Delete the old database file if it exists
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")

    # Create a connection to the SQLite database
    # This will create the file if it doesn't exist
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    print(f"Database created: {DB_FILE}")

    # Read and execute the schema SQL file
    try:
        with open(SCHEMA_FILE, 'r', encoding='utf-8-sig') as f:
            schema_sql = f.read()
        # SQLite doesn't support AUTO_INCREMENT in the same way as MySQL.
        # INTEGER PRIMARY KEY is sufficient to create an auto-incrementing alias for rowid.
        # Also, SQLite doesn't have DECIMAL, so we use REAL or INTEGER. Using INTEGER for money.
        schema_sql = schema_sql.replace('AUTO_INCREMENT', '')
        schema_sql = schema_sql.replace('DECIMAL(18, 0)', 'INTEGER')
        cursor.executescript(schema_sql)
        print(f"Successfully executed schema from {SCHEMA_FILE}")
    except FileNotFoundError:
        print(f"Error: {SCHEMA_FILE} not found.")
        conn.close()
        return
    except Exception as e:
        print(f"An error occurred while executing the schema: {e}")
        conn.close()
        return


    # Read and execute the data SQL file
    try:
        with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
            data_sql = f.read()
        cursor.executescript(data_sql)
        print(f"Successfully inserted data from {DATA_FILE}")
    except FileNotFoundError:
        print(f"Error: {DATA_FILE} not found.")
    except Exception as e:
        print(f"An error occurred while inserting data: {e}")


    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("Database setup complete.")

if __name__ == "__main__":
    create_database()
