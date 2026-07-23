import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "beccs.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    # =====================================================
    # TABELA DE DELIVERABLES
    # =====================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS deliverables (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_task_id INTEGER,
            title TEXT NOT NULL,
            discipline TEXT,
            description TEXT,
            manager TEXT,
            priority TEXT,
            status TEXT,
            progress INTEGER DEFAULT 0,
            deadline TEXT,
            google_drive TEXT
        )
        """
    )

    # =====================================================
    # TABELA DO CRONOGRAMA
    # =====================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            task_name TEXT NOT NULL,
            start_date TEXT,
            finish_date TEXT,
            duration TEXT,
            progress INTEGER DEFAULT 0,
            responsible TEXT,
            predecessor TEXT,
            summary INTEGER DEFAULT 0,
            milestone INTEGER DEFAULT 0,
            outline_level INTEGER DEFAULT 1,
            discipline TEXT,
            imported_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS project_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            project_name TEXT NOT NULL,
            subtitle TEXT,
            client TEXT,
            project_manager TEXT,
            phase TEXT,
            start_date TEXT,
            end_date TEXT,
            drive_link TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO project_settings (
            id,
            project_name,
            subtitle,
            client,
            project_manager,
            phase,
            start_date,
            end_date,
            drive_link,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            1,
            "BECCS Baseline Manager",
            "Performance & Well Integrity",
            "Cliente não definido",
            "Bruno Batista",
            "Desenvolvimento da Baseline",
            "2026-08-01",
            "2026-12-31",
            "",
        ),
    )

    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS meetings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        meeting_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        duration_minutes INTEGER DEFAULT 60,
        participants TEXT,
        description TEXT,
        recording_link TEXT,
        status TEXT NOT NULL DEFAULT 'Agendada',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """
)

    # =====================================================
    # TABELA DE PASTAS / DOCUMENTOS
    # =====================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS document_folders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            discipline TEXT,
            description TEXT,
            drive_link TEXT NOT NULL,
            responsible TEXT,
            updated_at TEXT
        )
        """
    )

    conn.commit()

    # =====================================================
    # DADOS INICIAIS DE TESTE
    # =====================================================

    cursor.execute("SELECT COUNT(*) FROM deliverables")
    total_deliverables = cursor.fetchone()[0]

    if total_deliverables == 0:
        cursor.executemany(
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
            [
                (
                    None,
                    "Deliverability Study",
                    "Performance",
                    "Avaliação de desempenho e capacidade do poço.",
                    "Bruno",
                    "Alta",
                    "Em andamento",
                    45,
                    "2026-09-20",
                    "",
                ),
                (
                    None,
                    "Injectivity Analysis",
                    "Performance",
                    "Avaliação da capacidade de injeção de CO₂.",
                    "Maria",
                    "Alta",
                    "Não iniciado",
                    0,
                    "2026-09-25",
                    "",
                ),
                (
                    None,
                    "Cement Integrity",
                    "Integridade",
                    "Avaliação da integridade da cimentação.",
                    "João",
                    "Média",
                    "Concluído",
                    100,
                    "2026-09-10",
                    "",
                ),
            ],
        )

    conn.commit()
    conn.close()
