from database.database import get_connection


class DeliverableRepository:

    @staticmethod
    def get_all():

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT *

            FROM deliverables

            ORDER BY deadline

        """)

        data = cursor.fetchall()

        conn.close()

        return data


    @staticmethod
    def get_by_id(deliverable_id):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            SELECT *

            FROM deliverables

            WHERE id = ?

        """, (deliverable_id,))

        data = cursor.fetchone()

        conn.close()

        return data


    @staticmethod
    def insert(
        title,
        discipline,
        description,
        manager,
        priority,
        status,
        progress,
        deadline,
        google_drive
    ):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            INSERT INTO deliverables
            (
                title,
                discipline,
                description,
                manager,
                priority,
                status,
                progress,
                deadline,
                google_drive
            )

            VALUES
            (?,?,?,?,?,?,?,?,?)

        """,

        (
            title,
            discipline,
            description,
            manager,
            priority,
            status,
            progress,
            deadline,
            google_drive
        ))

        conn.commit()

        conn.close()

    @staticmethod
    def update(
        deliverable_id,
        title,
        discipline,
        description,
        manager,
        priority,
        status,
        progress,
        deadline,
        google_drive,
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE deliverables
            SET
                title = ?,
                discipline = ?,
                description = ?,
                manager = ?,
                priority = ?,
                status = ?,
                progress = ?,
                deadline = ?,
                google_drive = ?
            WHERE id = ?
            """,
            (
                title,
                discipline,
                description,
                manager,
                priority,
                status,
                progress,
                deadline,
                google_drive,
                deliverable_id,
            ),
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
            FROM deliverables
            WHERE discipline IS NOT NULL
              AND TRIM(discipline) <> ''
            ORDER BY discipline
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return [row["discipline"] for row in rows]

    @staticmethod
    def delete(deliverable_id):

        conn = get_connection()

        cursor = conn.cursor()

        cursor.execute("""

            DELETE FROM deliverables

            WHERE id = ?

        """, (deliverable_id,))

        conn.commit()

        conn.close()