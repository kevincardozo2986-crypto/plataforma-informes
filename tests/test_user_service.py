import pytest

from app.database import database
from app.services import auth_service, user_service


@pytest.fixture
def users(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "app.db")
    auth_service.initialize_database()
    admin = auth_service.create_user("admin", "Admin123", "Administrador", "admin")
    normal = auth_service.create_user("normal", "Normal123", "Usuario Normal")
    return admin, normal


def test_admin_puede_hacer_crud(users):
    admin, _ = users

    created = user_service.create_managed_user(
        admin, "nuevo", "Clave123", "Usuario Nuevo"
    )
    assert len(user_service.list_users(admin)) == 3

    updated = user_service.update_user(
        admin, created["id"], "nuevo", "Nombre Editado", "user", False
    )
    assert updated["full_name"] == "Nombre Editado"
    assert updated["is_active"] is False

    user_service.delete_user(admin, created["id"])
    assert len(user_service.list_users(admin)) == 2


def test_usuario_normal_no_puede_gestionar(users):
    _, normal = users

    with pytest.raises(PermissionError):
        user_service.list_users(normal)


def test_admin_no_puede_eliminarse(users):
    admin, _ = users

    with pytest.raises(ValueError, match="propio usuario"):
        user_service.delete_user(admin, admin["id"])
