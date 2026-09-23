import pytest

from app.database import database
from app.services import auth_service
from app.services.report_option_service import (
    add_report_option,
    delete_report_option,
    list_report_options,
    update_report_option,
)


@pytest.fixture
def usuarios(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "app.db")
    auth_service.initialize_database()
    administrador = auth_service.create_user(
        "admin", "Admin123", "Administrador", "admin"
    )
    usuario = auth_service.create_user("usuario", "Usuario123", "Usuario")
    return administrador, usuario


def test_administrador_puede_agregar_opcion(usuarios):
    administrador, _ = usuarios

    add_report_option(administrador, "program", "Derecho")

    assert "Derecho" in list_report_options("program")


@pytest.mark.parametrize("categoria,valor", [
    ("program", "Derecho"), ("period", "2028-2"),
    ("level", "Educación continua"), ("modality", "A distancia"),
])
def test_usuario_normal_puede_agregar_opcion(usuarios, categoria, valor):
    _, usuario = usuarios
    add_report_option(usuario, categoria, valor)
    assert valor in list_report_options(categoria)


@pytest.mark.parametrize("usuario", [None, {}, {"role": "user", "is_active": False}])
def test_sin_sesion_activa_no_puede_agregar(usuarios, usuario):
    with pytest.raises(PermissionError):
        add_report_option(usuario, "program", "Derecho")
    with pytest.raises(PermissionError):
        update_report_option(usuario, "level", "Pregrado", "Otro")
    with pytest.raises(PermissionError):
        delete_report_option(usuario, "level", "Pregrado")


@pytest.mark.parametrize("categoria,original,nuevo", [
    ("period", "2028-1", "2028-2"),
    ("program", "Derecho", "Derecho Virtual"),
    ("level", "Educación continua", "Extensión"),
    ("modality", "A distancia", "Mixta"),
])
def test_usuario_normal_puede_editar_opcion(usuarios, categoria, original, nuevo):
    _, usuario = usuarios
    add_report_option(usuario, categoria, original)
    update_report_option(usuario, categoria, original, nuevo)
    assert nuevo in list_report_options(categoria)
    assert original not in list_report_options(categoria)
    delete_report_option(usuario, categoria, nuevo)
    assert nuevo not in list_report_options(categoria)


def test_no_permite_opciones_duplicadas(usuarios):
    administrador, _ = usuarios

    with pytest.raises(ValueError, match="ya existe"):
        add_report_option(administrador, "level", "pregrado")


@pytest.mark.parametrize(
    "periodo_invalido",
    ["2028-9", "20296-3", "26-1", "2026-0", "2026-3", "2026/1"],
)
def test_periodo_debe_tener_ano_y_semestre_validos(usuarios, periodo_invalido):
    administrador, _ = usuarios

    with pytest.raises(ValueError, match="AAAA-S"):
        add_report_option(administrador, "period", periodo_invalido)


def test_acepta_periodo_con_formato_valido(usuarios):
    administrador, _ = usuarios

    add_report_option(administrador, "period", "2028-2")

    assert "2028-2" in list_report_options("period")


def test_administrador_puede_eliminar_opcion(usuarios):
    administrador, _ = usuarios
    add_report_option(administrador, "program", "Derecho")

    delete_report_option(administrador, "program", "Derecho")

    assert "Derecho" not in list_report_options("program")


def test_usuario_normal_puede_eliminar_opcion(usuarios):
    _, usuario = usuarios

    delete_report_option(usuario, "program", "Ingeniería de Sistemas")
    assert "Ingeniería de Sistemas" not in list_report_options("program")


def test_no_permite_eliminar_la_ultima_opcion(usuarios):
    administrador, _ = usuarios
    for opcion in list_report_options("level")[1:]:
        delete_report_option(administrador, "level", opcion)

    with pytest.raises(ValueError, match="al menos una"):
        delete_report_option(administrador, "level", "Pregrado")


def test_administrador_puede_editar_opcion(usuarios):
    administrador, _ = usuarios
    add_report_option(administrador, "program", "Derecho")

    update_report_option(administrador, "program", "Derecho", "Derecho Virtual")

    opciones = list_report_options("program")
    assert "Derecho" not in opciones
    assert "Derecho Virtual" in opciones


def test_edicion_de_periodo_conserva_formato_valido(usuarios):
    administrador, _ = usuarios

    with pytest.raises(ValueError, match="AAAA-S"):
        update_report_option(administrador, "period", "2026-1", "2026-9")
