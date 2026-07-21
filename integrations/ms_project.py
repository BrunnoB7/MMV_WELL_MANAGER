import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from database.database import get_connection


PROJECT_FILE = Path("data/project/baseline_schedule.xlsx")
MAPPING_FILE = Path("config/project_mapping.json")


def project_exists():
    return PROJECT_FILE.exists() and PROJECT_FILE.stat().st_size > 0


def load_mapping():
    if not MAPPING_FILE.exists():
        raise FileNotFoundError(
            "Arquivo config/project_mapping.json não encontrado."
        )

    with open(MAPPING_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def normalize_boolean(value):
    if pd.isna(value):
        return 0

    normalized = str(value).strip().lower()

    true_values = {
        "true",
        "sim",
        "yes",
        "1",
        "-1",
        "verdadeiro",
    }

    return 1 if normalized in true_values else 0


def normalize_progress(value):
    if pd.isna(value):
        return 0

    if isinstance(value, str):
        value = value.replace("%", "").replace(",", ".").strip()

    try:
        progress = float(value)

        # Algumas exportações retornam 0.50 em vez de 50.
        if 0 < progress <= 1:
            progress *= 100

        return max(0, min(100, int(round(progress))))

    except (TypeError, ValueError):
        return 0


def normalize_date(value):
    if pd.isna(value):
        return None

    date = pd.to_datetime(value, errors="coerce")

    if pd.isna(date):
        return None

    return date.strftime("%Y-%m-%d")


def load_project(source=None):
    source = source or PROJECT_FILE

    try:
        return pd.read_excel(
            source,
            engine="openpyxl",
        )

    except Exception as error:
        raise RuntimeError(
            f"Não foi possível ler o Excel do Microsoft Project: {error}"
        ) from error


def validate_columns(df, mapping):
    required_keys = [
        "task_id",
        "task_name",
        "start",
        "finish",
        "progress",
        "summary",
        "milestone",
        "outline_level",
    ]

    missing = []

    for key in required_keys:
        column_name = mapping.get(key)

        if not column_name or column_name not in df.columns:
            missing.append(column_name or key)

    if missing:
        raise ValueError(
            "Colunas não encontradas no Excel: "
            + ", ".join(missing)
        )


def column_value(row, mapping, key, default=None):
    column_name = mapping.get(key)

    if not column_name or column_name not in row.index:
        return default

    value = row[column_name]

    if pd.isna(value):
        return default

    return value


def prepare_schedule_dataframe(source=None):
    df = load_project(source)
    mapping = load_mapping()

    validate_columns(df, mapping)

    records = []
    current_discipline = "Não definida"

    for _, row in df.iterrows():
        task_name = column_value(
            row,
            mapping,
            "task_name",
            "",
        )

        if not str(task_name).strip():
            continue

        outline_level = column_value(
            row,
            mapping,
            "outline_level",
            1,
        )

        try:
            outline_level = int(outline_level)
        except (TypeError, ValueError):
            outline_level = 1

        summary = normalize_boolean(
            column_value(row, mapping, "summary", 0)
        )

        milestone = normalize_boolean(
            column_value(row, mapping, "milestone", 0)
        )

        # Toda tarefa de nível 1 representa uma disciplina.
        if outline_level == 1:
            current_discipline = str(task_name).strip()

        task_id = column_value(row, mapping, "task_id")

        try:
            task_id = int(task_id)
        except (TypeError, ValueError):
            task_id = None

        records.append(
            {
                "task_id": task_id,
                "task_name": str(task_name).strip(),
                "start_date": normalize_date(
                    column_value(row, mapping, "start")
                ),
                "finish_date": normalize_date(
                    column_value(row, mapping, "finish")
                ),
                "duration": str(
                    column_value(
                        row,
                        mapping,
                        "duration",
                        "",
                    )
                ),
                "progress": normalize_progress(
                    column_value(row, mapping, "progress", 0)
                ),
                "responsible": str(
                    column_value(
                        row,
                        mapping,
                        "resource",
                        "",
                    )
                ),
                "predecessor": str(
                    column_value(
                        row,
                        mapping,
                        "predecessor",
                        "",
                    )
                ),
                "summary": summary,
                "milestone": milestone,
                "outline_level": outline_level,
                "discipline": current_discipline,
            }
        )

    return pd.DataFrame(records)


def status_from_progress(progress, finish_date):
    if progress >= 100:
        return "Concluído"

    if finish_date:
        deadline = pd.to_datetime(finish_date, errors="coerce")

        if not pd.isna(deadline) and deadline.date() < datetime.now().date():
            return "Atrasado"

    if progress > 0:
        return "Em andamento"

    return "Não iniciado"


def import_project_to_database(source=None):
    schedule_df = prepare_schedule_dataframe(source)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM schedule")

        imported_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for _, task in schedule_df.iterrows():
            cursor.execute(
                """
                INSERT INTO schedule (
                    task_id,
                    task_name,
                    start_date,
                    finish_date,
                    duration,
                    progress,
                    responsible,
                    predecessor,
                    summary,
                    milestone,
                    outline_level,
                    discipline,
                    imported_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task["task_id"],
                    task["task_name"],
                    task["start_date"],
                    task["finish_date"],
                    task["duration"],
                    task["progress"],
                    task["responsible"],
                    task["predecessor"],
                    task["summary"],
                    task["milestone"],
                    task["outline_level"],
                    task["discipline"],
                    imported_at,
                ),
            )

        sync_deliverables(cursor, schedule_df)

        conn.commit()

        return {
            "success": True,
            "tasks": len(schedule_df),
            "deliverables": len(
                schedule_df[
                    (schedule_df["summary"] == 1)
                    & (schedule_df["outline_level"] == 2)
                ]
            ),
            "milestones": int(schedule_df["milestone"].sum()),
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def sync_deliverables(cursor, schedule_df):
    deliverables = schedule_df[
        (schedule_df["summary"] == 1)
        & (schedule_df["outline_level"] == 2)
    ]

    for _, deliverable in deliverables.iterrows():
        status = status_from_progress(
            deliverable["progress"],
            deliverable["finish_date"],
        )

        cursor.execute(
            """
            SELECT id
            FROM deliverables
            WHERE project_task_id = ?
            """,
            (deliverable["task_id"],),
        )

        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                """
                UPDATE deliverables
                SET
                    title = ?,
                    discipline = ?,
                    manager = ?,
                    status = ?,
                    progress = ?,
                    deadline = ?
                WHERE project_task_id = ?
                """,
                (
                    deliverable["task_name"],
                    deliverable["discipline"],
                    deliverable["responsible"],
                    status,
                    deliverable["progress"],
                    deliverable["finish_date"],
                    deliverable["task_id"],
                ),
            )

        else:
            cursor.execute(
                """
                INSERT INTO deliverables (
                    project_task_id,
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
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    deliverable["task_id"],
                    deliverable["task_name"],
                    deliverable["discipline"],
                    "Importado automaticamente do Microsoft Project.",
                    deliverable["responsible"],
                    "Média",
                    status,
                    deliverable["progress"],
                    deliverable["finish_date"],
                    "",
                ),
            )


def get_project_info():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM schedule")
    tasks = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM schedule WHERE milestone = 1"
    )
    milestones = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT MAX(imported_at)
        FROM schedule
        """
    )
    last_import = cursor.fetchone()[0]

    conn.close()

    return {
        "exists": project_exists(),
        "tasks": tasks,
        "milestones": milestones,
        "last_import": last_import,
    }