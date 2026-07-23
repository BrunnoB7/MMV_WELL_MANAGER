from database.database import get_connection


class MeetingRepository:

    @staticmethod
    def get_all():
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status,
                    created_at,
                    updated_at
                FROM meetings
                ORDER BY
                    meeting_date ASC,
                    start_time ASC
                """
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def get_by_id(meeting_id):
        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    id,
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status,
                    created_at,
                    updated_at
                FROM meetings
                WHERE id = ?
                """,
                (meeting_id,),
            ).fetchone()

            return dict(row) if row else None

        finally:
            connection.close()

    @staticmethod
    def get_scheduled():
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status
                FROM meetings
                WHERE LOWER(TRIM(status)) = 'agendada'
                ORDER BY
                    meeting_date ASC,
                    start_time ASC
                """
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def get_completed():
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status
                FROM meetings
                WHERE LOWER(TRIM(status)) = 'realizada'
                ORDER BY
                    meeting_date DESC,
                    start_time DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def get_by_date(meeting_date):
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status
                FROM meetings
                WHERE meeting_date = ?
                  AND LOWER(TRIM(status)) != 'cancelada'
                ORDER BY start_time ASC
                """,
                (meeting_date,),
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def insert(
        title,
        meeting_date,
        start_time,
        duration_minutes,
        participants,
        description,
        recording_link,
        status,
    ):
        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO meetings (
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status,
                ),
            )

            connection.commit()
            return cursor.lastrowid

        finally:
            connection.close()

    @staticmethod
    def update(
        meeting_id,
        title,
        meeting_date,
        start_time,
        duration_minutes,
        participants,
        description,
        recording_link,
        status,
    ):
        connection = get_connection()

        try:
            connection.execute(
                """
                UPDATE meetings
                SET
                    title = ?,
                    meeting_date = ?,
                    start_time = ?,
                    duration_minutes = ?,
                    participants = ?,
                    description = ?,
                    recording_link = ?,
                    status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (
                    title,
                    meeting_date,
                    start_time,
                    duration_minutes,
                    participants,
                    description,
                    recording_link,
                    status,
                    meeting_id,
                ),
            )

            connection.commit()

        finally:
            connection.close()

    @staticmethod
    def delete(meeting_id):
        connection = get_connection()

        try:
            connection.execute(
                """
                DELETE FROM meetings
                WHERE id = ?
                """,
                (meeting_id,),
            )

            connection.commit()

        finally:
            connection.close()
