"""Persistencia del avance para reanudar informes incompletos."""

from app.database.database import get_connection


def save_process_progress(
    usuario,
    period,
    level,
    modality,
    program,
    base_directory,
    source_csv,
    workbook_path,
    completed_step,
    status="in_progress",
    error_message=None,
):
    if not usuario or not usuario.get("id"):
        raise ValueError("No se pudo identificar al usuario del proceso.")
    with get_connection() as conexion:
        conexion.execute(
            """
            INSERT INTO report_processes (
                user_id, period, level, modality, program, base_directory,
                source_csv, workbook_path, completed_step, status, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(workbook_path) DO UPDATE SET
                user_id = excluded.user_id,
                period = excluded.period,
                level = excluded.level,
                modality = excluded.modality,
                program = excluded.program,
                base_directory = excluded.base_directory,
                source_csv = excluded.source_csv,
                completed_step = excluded.completed_step,
                status = excluded.status,
                error_message = excluded.error_message,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                usuario["id"], period, level, modality, program,
                str(base_directory), str(source_csv), str(workbook_path),
                completed_step, status, error_message,
            ),
        )


def list_incomplete_processes(usuario):
    if not usuario:
        return []
    consulta = """
        SELECT id, user_id, period, level, modality, program, base_directory,
               source_csv, workbook_path, completed_step, status,
               error_message, updated_at
        FROM report_processes
        WHERE status != 'completed'
    """
    parametros = []
    if usuario.get("role") != "admin":
        consulta += " AND user_id = ?"
        parametros.append(usuario["id"])
    consulta += " ORDER BY updated_at DESC"
    with get_connection() as conexion:
        filas = conexion.execute(consulta, parametros).fetchall()
    return [dict(fila) for fila in filas]


def list_completed_processes(usuario):
    """Lista informes finalizados, respetando el alcance del usuario."""
    if not usuario:
        return []
    consulta = """
        SELECT report_processes.id, report_processes.user_id,
               report_processes.period, report_processes.level,
               report_processes.modality, report_processes.program,
               report_processes.base_directory, report_processes.source_csv,
               report_processes.workbook_path, report_processes.completed_step,
               report_processes.status, report_processes.updated_at,
               users.full_name AS owner_name
        FROM report_processes
        JOIN users ON users.id = report_processes.user_id
        WHERE report_processes.status = 'completed'
    """
    parametros = []
    if usuario.get("role") != "admin":
        consulta += " AND report_processes.user_id = ?"
        parametros.append(usuario["id"])
    consulta += " ORDER BY report_processes.updated_at DESC"
    with get_connection() as conexion:
        filas = conexion.execute(consulta, parametros).fetchall()
    return [dict(fila) for fila in filas]


def mark_process_completed(workbook_path, saved_path=None):
    with get_connection() as conexion:
        ruta_guardada = str(saved_path or workbook_path)
        if saved_path:
            conexion.execute(
                "DELETE FROM report_processes WHERE workbook_path = ? AND workbook_path != ?",
                (ruta_guardada, str(workbook_path)),
            )
        conexion.execute(
            """
            UPDATE report_processes
            SET status = 'completed', error_message = NULL,
                workbook_path = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE workbook_path = ?
            """,
            (ruta_guardada, str(workbook_path)),
        )
