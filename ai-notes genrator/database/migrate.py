"""
Run once to bring an existing database up to date.
Safe to run multiple times — uses ALTER TABLE only when the column is missing.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def column_exists(cursor, table, column):
    cursor.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cursor.fetchall())


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    migrations = [
        ("notes", "is_favorite", "INTEGER DEFAULT 0"),
        ("notes", "tags",        "TEXT    DEFAULT ''"),
    ]

    for table, col, definition in migrations:
        if not column_exists(cursor, table, col):
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {definition}")
            print(f"  + Added column '{col}' to '{table}'")
        else:
            print(f"  ✓ Column '{col}' already exists in '{table}'")

    conn.commit()
    conn.close()
    print("Migration complete.")


if __name__ == "__main__":
    migrate()