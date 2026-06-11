from database.db import get_connection


class NoteModel:

    @staticmethod
    def create_note(
        user_id,
        title,
        original_content,
        summary,
        detailed_notes,
        key_concepts,
        revision_notes,
        flashcards,
        quiz_questions,
        language="English"
    ):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO notes
            (
                user_id,
                title,
                original_content,
                summary,
                detailed_notes,
                key_concepts,
                revision_notes,
                flashcards,
                quiz_questions,
                language
            )

            VALUES (?,?,?,?,?,?,?,?,?,?)
            """,

            (
                user_id,
                title,
                original_content,
                summary,
                detailed_notes,
                key_concepts,
                revision_notes,
                flashcards,
                quiz_questions,
                language
            )
        )

        conn.commit()

        conn.close()

    @staticmethod
    def get_user_notes(user_id):

        conn = get_connection()

        conn.row_factory = lambda cursor, row: {
            col[0]: row[idx]
            for idx, col in enumerate(cursor.description)
        }

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM notes
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,)
        )

        notes = cursor.fetchall()

        conn.close()

        return notes

    @staticmethod
    def get_note_by_id(note_id):

        conn = get_connection()

        conn.row_factory = lambda cursor, row: {
            col[0]: row[idx]
            for idx, col in enumerate(cursor.description)
        }

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM notes
            WHERE id = ?
            """,
            (note_id,)
        )

        note = cursor.fetchone()

        conn.close()

        return note

    @staticmethod
    def delete_note(note_id):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM notes
            WHERE id = ?
            """,
            (note_id,)
        )

        conn.commit()

        conn.close()