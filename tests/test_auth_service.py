import sqlite3

import pytest

from app.database import database
from app.services import auth_service


@pytest.fixture(autouse=True)
def isolated_database(tmp_path, monkeypatch):
    test_database = tmp_path / "app.db"
    monkeypatch.setattr(database, "DATABASE_PATH", test_database)
    auth_service.initialize_database()
    return test_database


def test_login_correcto():
    auth_service.create_user("kevin", "ClaveSegura1!", "Kevin Prueba")

    user = auth_service.authenticate_user("kevin", "ClaveSegura1!")

    assert user is not None
    assert user["username"] == "kevin"
    assert "password_hash" not in user


def test_password_incorrecta():
    auth_service.create_user("kevin", "ClaveSegura1!", "Kevin Prueba")

    assert auth_service.authenticate_user("kevin", "incorrecta") is None


def test_usuario_inexistente():
    assert auth_service.authenticate_user("nadie", "cualquiera") is None


def test_usuario_desactivado():
    auth_service.create_user("kevin", "ClaveSegura1!", "Kevin Prueba")
    with database.get_connection() as connection:
        connection.execute(
            "UPDATE users SET is_active = ? WHERE username = ?",
            (0, "kevin"),
        )

    assert auth_service.authenticate_user("kevin", "ClaveSegura1!") is None


def test_username_duplicado():
    auth_service.create_user("kevin", "ClaveSegura1!", "Kevin Prueba")

    with pytest.raises(ValueError, match="ya existe"):
        auth_service.create_user("KEVIN", "OtraClave1!", "Otro Kevin")


def test_password_se_almacena_como_hash():
    auth_service.create_user("kevin", "ClaveSegura1!", "Kevin Prueba")
    with database.get_connection() as connection:
        stored = connection.execute(
            "SELECT password_hash FROM users WHERE username = ?", ("kevin",)
        ).fetchone()["password_hash"]

    assert stored != "ClaveSegura1!"
    assert stored.startswith("scrypt$")


def test_crea_admin_inicial_una_sola_vez():
    auth_service.initialize_auth()
    auth_service.initialize_auth()

    admin = auth_service.authenticate_user(
        auth_service.DEFAULT_ADMIN_USERNAME,
        auth_service.DEFAULT_ADMIN_PASSWORD,
    )
    assert admin is not None
    assert admin["role"] == "admin"

    with sqlite3.connect(database.DATABASE_PATH) as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM users WHERE username = ?",
            (auth_service.DEFAULT_ADMIN_USERNAME,),
        ).fetchone()[0]
    assert count == 1
