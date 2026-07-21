from datetime import date, datetime

from database.database import get_connection


class DashboardService:

    @staticmethod
    def get_project_settings():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM project_settings
            WHERE id = 1
            """
        )

        settings = cursor.fetchone()
        conn.close()

        return dict(settings) if settings else {}


    @staticmethod
    def update_project_settings(
        project_name,
        subtitle,
        client,
        project_manager,
        phase,
        start_date,
        end_date,
        drive_link,
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE project_settings
            SET
                project_name = ?,
                subtitle = ?,
                client = ?,
                project_manager = ?,
                phase = ?,
                start_date = ?,
                end_date = ?,
                drive_link = ?,
                updated_at = ?
            WHERE id = 1
            """,
            (
                project_name,
                subtitle,
                client,
                project_manager,
                phase,
                start_date,
                end_date,
                drive_link,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        conn.commit()
        conn.close()


    @staticmethod
    def get_kpis():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM deliverables")
        total = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM deliverables
            WHERE status = 'Em andamento'
            """
        )
        in_progress = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM deliverables
            WHERE status = 'Concluído'
               OR progress >= 100
            """
        )
        completed = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM deliverables
            WHERE progress < 100
              AND (
                    status = 'Atrasado'
                    OR date(deadline) < date('now')
              )
            """
        )
        delayed = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COALESCE(ROUND(AVG(progress), 0), 0)
            FROM deliverables
            """
        )
        average_progress = cursor.fetchone()[0]

        conn.close()

        return {
            "total": int(total or 0),
            "in_progress": int(in_progress or 0),
            "completed": int(completed or 0),
            "delayed": int(delayed or 0),
            "average_progress": int(average_progress or 0),
        }


    @staticmethod
    def get_days_remaining(end_date):
        if not end_date:
            return None

        try:
            project_end = date.fromisoformat(end_date)
            return (project_end - date.today()).days
        except ValueError:
            return None


    @staticmethod
    def get_next_milestones(limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                task_name,
                finish_date,
                progress,
                responsible,
                discipline
            FROM schedule
            WHERE milestone = 1
              AND finish_date IS NOT NULL
              AND date(finish_date) >= date('now')
            ORDER BY date(finish_date)
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]


    @staticmethod
    def get_critical_pending(limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                title,
                discipline,
                manager,
                deadline,
                status,
                progress
            FROM deliverables
            WHERE progress < 100
              AND (
                    status = 'Atrasado'
                    OR date(deadline) < date('now')
              )
            ORDER BY date(deadline)
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]


    @staticmethod
    def get_priorities(limit=5):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                title,
                discipline,
                manager,
                deadline,
                progress,
                priority
            FROM deliverables
            WHERE progress < 100
            ORDER BY
                CASE priority
                    WHEN 'Crítica' THEN 1
                    WHEN 'Alta' THEN 2
                    WHEN 'Média' THEN 3
                    WHEN 'Baixa' THEN 4
                    ELSE 5
                END,
                date(deadline)
            LIMIT ?
            """,
            (limit,),
        )

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]


    @staticmethod
    def get_last_sync():
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT MAX(imported_at)
            FROM schedule
            """
        )

        last_sync = cursor.fetchone()[0]
        conn.close()

        return last_sync