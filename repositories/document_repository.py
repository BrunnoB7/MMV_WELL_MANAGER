from database.database import get_connection


class DocumentRepository:

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM document_folders
            ORDER BY discipline, name
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    @staticmethod
    def get_by_id(folder_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM document_folders
            WHERE id = ?
            """,
            (folder_id,),
        )

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    @staticmethod
    def insert(
        name,
        discipline,
        description,
        drive_link,
        responsible,
        updated_at,
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO document_folders (
                name,
                discipline,
                description,
                drive_link,
                responsible,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                discipline,
                description,
                drive_link,
                responsible,
                updated_at,
            ),
        )

        folder_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return folder_id

    @staticmethod
    def update(
        folder_id,
        name,
        discipline,
        description,
        drive_link,
        responsible,
        updated_at,
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE document_folders
            SET
                name = ?,
                discipline = ?,
                description = ?,
                drive_link = ?,
                responsible = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                name,
                discipline,
                description,
                drive_link,
                responsible,
                updated_at,
                folder_id,
            ),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def delete(folder_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM document_folders
            WHERE id = ?
            """,
            (folder_id,),
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_disciplines():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT DISTINCT discipline
            FROM document_folders
            WHERE discipline IS NOT NULL
              AND TRIM(discipline) <> ''
            ORDER BY discipline
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return [row["discipline"] for row in rows]