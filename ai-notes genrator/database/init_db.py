from db import get_connection

conn = get_connection()

cursor = conn.cursor()

# Users Table

cursor.execute("""

CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)

""")

# Notes Table

cursor.execute("""

CREATE TABLE IF NOT EXISTS notes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER,

    title TEXT,

    original_content TEXT,

    summary TEXT,

    detailed_notes TEXT,

    key_concepts TEXT,

    revision_notes TEXT,

    flashcards TEXT,

    quiz_questions TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(user_id)

    REFERENCES users(id)

)

""")

conn.commit()

conn.close()

print("Database Created Successfully")