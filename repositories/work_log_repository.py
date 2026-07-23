from database.database import get_connection


class WorkLogRepository:

    @staticmethod
    def create(
        deliverable_id,
        collaborator,
        worked_hours,
        work_date,
        description,
    ):
        connection = get_connection()

        try:
            cursor = connection.execute(
                """
                INSERT INTO deliverable_work_logs (
                    deliverable_id,
                    collaborator,
                    worked_hours,
                    work_date,
                    description
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    deliverable_id,
                    collaborator,
                    worked_hours,
                    work_date,
                    description,
                ),
            )

            connection.commit()

            return cursor.lastrowid

        finally:
            connection.close()

    @staticmethod
    def get_by_deliverable(deliverable_id):
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    id,
                    deliverable_id,
                    collaborator,
                    worked_hours,
                    work_date,
                    description,
                    created_at
                FROM deliverable_work_logs
                WHERE deliverable_id = ?
                ORDER BY
                    work_date DESC,
                    created_at DESC
                """,
                (deliverable_id,),
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def get_all_with_deliverable():
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    work_log.id,
                    work_log.deliverable_id,
                    work_log.collaborator,
                    work_log.worked_hours,
                    work_log.work_date,
                    work_log.description,
                    work_log.created_at,

                    deliverable.title
                        AS deliverable_title,

                    deliverable.discipline
                        AS deliverable_discipline,

                    deliverable.status
                        AS deliverable_status,

                    deliverable.deadline
                        AS deliverable_deadline

                FROM deliverable_work_logs AS work_log

                INNER JOIN deliverables AS deliverable
                    ON deliverable.id =
                        work_log.deliverable_id

                ORDER BY
                    work_log.work_date DESC,
                    work_log.created_at DESC
                """
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def get_total_by_deliverable(deliverable_id):
        connection = get_connection()

        try:
            row = connection.execute(
                """
                SELECT
                    COALESCE(
                        SUM(worked_hours),
                        0
                    ) AS total_hours
                FROM deliverable_work_logs
                WHERE deliverable_id = ?
                """,
                (deliverable_id,),
            ).fetchone()

            return float(
                row["total_hours"] or 0
            )

        finally:
            connection.close()

    @staticmethod
    def get_summary_by_deliverable(
        deliverable_id
    ):
        connection = get_connection()

        try:
            rows = connection.execute(
                """
                SELECT
                    collaborator,
                    SUM(worked_hours)
                        AS total_hours
                FROM deliverable_work_logs
                WHERE deliverable_id = ?
                GROUP BY collaborator
                ORDER BY total_hours DESC
                """,
                (deliverable_id,),
            ).fetchall()

            return [dict(row) for row in rows]

        finally:
            connection.close()

    @staticmethod
    def delete(work_log_id):
        connection = get_connection()

        try:
            connection.execute(
                """
                DELETE FROM deliverable_work_logs
                WHERE id = ?
                """,
                (work_log_id,),
            )

            connection.commit()

        finally:
            connection.close()
