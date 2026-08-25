import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


# Partimos desde este archivo y subimos hasta la carpeta principal del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "app.db"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Abre una conexión y garantiza que se cierre al terminar."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(DATABASE_PATH)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def initialize_database() -> None:
    """Crea las tablas y opciones iniciales de la aplicación."""
    with get_connection() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL COLLATE NOCASE UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                is_active INTEGER NOT NULL DEFAULT 1
                    CHECK (is_active IN (0, 1)),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS report_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                value TEXT NOT NULL COLLATE NOCASE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(category, value)
            )
            """
        )
        opciones_iniciales = {
            "period": ("2025-1", "2025-2", "2026-1", "2026-2"),
            "level": ("Pregrado", "Posgrado"),
            "modality": ("Presencial", "Virtual", "Presencial-Virtual"),
            "program": (
                "Ingeniería de Sistemas",
                "Ingeniería Industrial",
                "Administración de Empresas",
            ),
        }
        for categoria, valores in opciones_iniciales.items():
            conexion.executemany(
                "INSERT OR IGNORE INTO report_options (category, value) VALUES (?, ?)",
                ((categoria, valor) for valor in valores),
            )
