import sqlite3

from app.database.database import get_connection
from app.models.user import user_to_dict
from app.services.auth_service import create_user, hash_password


VALID_ROLES = ("user", "admin")


def require_admin(current_user):
    """Impide ejecutar el CRUD si el usuario actual no es administrador."""
    if not current_user or current_user.get("role") != "admin":
        raise PermissionError("Se requieren permisos de administrador")


def list_users(current_user):
    require_admin(current_user)

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, username, full_name, role, is_active, created_at
            FROM users
            ORDER BY full_name COLLATE NOCASE
            """
        ).fetchall()

    return [user_to_dict(row) for row in rows]


def create_managed_user(current_user, username, password, full_name, role="user"):
    require_admin(current_user)
    if role not in VALID_ROLES:
        raise ValueError("El rol no es válido")
    return create_user(username, password, full_name, role)


def update_user(
    current_user,
    user_id,
    username,
    full_name,
    role,
    is_active,
    password="",
):
    require_admin(current_user)

    username = username.strip() if username else ""
    full_name = full_name.strip() if full_name else ""

    if not username or not full_name:
        raise ValueError("El usuario y el nombre completo son obligatorios")
    if role not in VALID_ROLES:
        raise ValueError("El rol no es válido")
    if user_id == current_user["id"] and (role != "admin" or not is_active):
        raise ValueError("No puedes quitar tus propios permisos ni desactivarte")

    try:
        with get_connection() as connection:
            exists = connection.execute(
                "SELECT id FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if exists is None:
                raise ValueError("El usuario no existe")

            connection.execute(
                """
                UPDATE users
                SET username = ?, full_name = ?, role = ?, is_active = ?
                WHERE id = ?
                """,
                (username, full_name, role, int(bool(is_active)), user_id),
            )

            if password:
                connection.execute(
                    "UPDATE users SET password_hash = ? WHERE id = ?",
                    (hash_password(password), user_id),
                )

            row = connection.execute(
                """
                SELECT id, username, full_name, role, is_active, created_at
                FROM users WHERE id = ?
                """,
                (user_id,),
            ).fetchone()
    except sqlite3.IntegrityError as error:
        raise ValueError("El nombre de usuario ya existe") from error

    return user_to_dict(row)


def delete_user(current_user, user_id):
    require_admin(current_user)

    if user_id == current_user["id"]:
        raise ValueError("No puedes eliminar tu propio usuario")

    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
        if cursor.rowcount == 0:
            raise ValueError("El usuario no existe")
