import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "inventory.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    schema_path = BASE_DIR / "schema.sql"

    with get_connection() as connection:
        schema = schema_path.read_text()
        connection.executescript(schema)

    print("SmartStock database initialized!")


if __name__ == "__main__":
    create_database()