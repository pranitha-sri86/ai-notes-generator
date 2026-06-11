from database.db import get_connection


class TutorModel:

    @staticmethod
    def save_chat(user_id, question, answer):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO tutor_chats
            (user_id, question, answer)
            VALUES (?, ?, ?)
            """,
            (user_id, question, answer)
        )

        conn.commit()

        conn.close()

    @staticmethod
    def get_user_chats(user_id):

        conn = get_connection()

        conn.row_factory = lambda cursor, row: {
            "id": row[0],
            "user_id": row[1],
            "question": row[2],
            "answer": row[3]
        }

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM tutor_chats
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        chats = cursor.fetchall()

        conn.close()

        return chats