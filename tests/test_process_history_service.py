from app.database import database
from app.services import auth_service
from app.services.process_history_service import (
    list_incomplete_processes,
    mark_process_completed,
    save_process_progress,
)


def test_guarda_reanuda_y_completa_un_proceso(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "app.db")
    auth_service.initialize_database()
    administrador = auth_service.create_user(
        "admin", "Admin123", "Administrador", "admin"
    )
    libro = tmp_path / "Informe_EN_PROCESO.xlsx"

    save_process_progress(
        administrador,
        "2026-1",
        "Pregrado",
        "Presencial",
        "Ingeniería de Sistemas",
        tmp_path,
        tmp_path / "moodle.csv",
        libro,
        2,
    )

    pendientes = list_incomplete_processes(administrador)
    assert len(pendientes) == 1
    assert pendientes[0]["completed_step"] == 2
    assert pendientes[0]["program"] == "Ingeniería de Sistemas"

    mark_process_completed(libro)
    assert list_incomplete_processes(administrador) == []


def test_usuario_solo_ve_sus_procesos_y_admin_ve_todos(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "app.db")
    auth_service.initialize_database()
    administrador = auth_service.create_user(
        "admin", "Admin123", "Administrador", "admin"
    )
    usuario_uno = auth_service.create_user("uno", "Usuario123", "Usuario Uno")
    usuario_dos = auth_service.create_user("dos", "Usuario123", "Usuario Dos")

    for usuario, nombre in ((usuario_uno, "uno"), (usuario_dos, "dos")):
        save_process_progress(
            usuario,
            "2026-1",
            "Pregrado",
            "Virtual",
            nombre,
            tmp_path,
            tmp_path / f"{nombre}.csv",
            tmp_path / f"{nombre}.xlsx",
            1,
            status="error",
            error_message="Fallo de prueba",
        )

    assert len(list_incomplete_processes(usuario_uno)) == 1
    assert list_incomplete_processes(usuario_uno)[0]["program"] == "uno"
    assert len(list_incomplete_processes(administrador)) == 2
