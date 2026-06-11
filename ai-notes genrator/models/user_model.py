from database.db import get_connection

class UserModel:

    @staticmethod
    def create_user(name, email, password):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name, email, password)
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_user_by_email(email):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = cursor.fetchone()

        conn.close()

        return user