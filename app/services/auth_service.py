import hashlib
import hmac
import os
import sqlite3

from app.database.database import get_connection, initialize_database
from app.models.user import user_to_dict


# Credenciales que se usan solamente para crear el primer administrador.
DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "Admin123"
DEFAULT_ADMIN_FULL_NAME = "Administrador"


def hash_password(password):
    """Convierte una contraseña en un hash seguro que no se puede descifrar."""
    if not password:
        raise ValueError("La contraseña no puede estar vacía")

    salt = os.urandom(16)
    password_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=32,
    )

    # Guardamos el algoritmo, su configuración, la sal y el hash.
    return f"scrypt$16384$8$1${salt.hex()}${password_hash.hex()}"


def password_is_correct(password, stored_hash):
    """Compara una contraseña escrita con el hash guardado en SQLite."""
    try:
        parts = stored_hash.split("$")
        algorithm = parts[0]
        salt = bytes.fromhex(parts[4])
        expected_hash = parts[5]

        if algorithm != "scrypt":
            return False

        calculated_hash = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=int(parts[1]),
            r=int(parts[2]),
            p=int(parts[3]),
            dklen=32,
        ).hex()

        return hmac.compare_digest(calculated_hash, expected_hash)
    except (AttributeError, IndexError, TypeError, ValueError):
        return False


def find_user_in_database(username):
    """Busca una fila completa de usuario para uso interno del servicio."""
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT id, username, password_hash, full_name,
                   role, is_active, created_at
            FROM users
            WHERE username = ? COLLATE NOCASE
            """,
            (username,),
        ).fetchone()


def get_user_by_username(username):
    """Busca un usuario y devuelve solamente sus datos públicos."""
    if not username or not username.strip():
        return None

    database_row = find_user_in_database(username.strip())
    if database_row is None:
        return None

    return user_to_dict(database_row)


def create_user(username, password, full_name, role="user"):
    """Crea un usuario y devuelve sus datos públicos."""
    initialize_database()

    username = username.strip() if username else ""
    full_name = full_name.strip() if full_name else ""
    role = role.strip() if role else ""

    if not username:
        raise ValueError("El nombre de usuario no puede estar vacío")
    if not full_name:
        raise ValueError("El nombre completo no puede estar vacío")
    if not role:
        raise ValueError("El rol no puede estar vacío")

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
                """,
                (username, hash_password(password), full_name, role),
            )

            new_user_id = cursor.lastrowid
            database_row = connection.execute(
                """
                SELECT id, username, full_name, role, is_active, created_at
                FROM users
                WHERE id = ?
                """,
                (new_user_id,),
            ).fetchone()
    except sqlite3.IntegrityError:
        raise ValueError("El nombre de usuario ya existe")

    return user_to_dict(database_row)


def authenticate_user(username, password):
    """Comprueba usuario, estado y contraseña."""
    if not username or not password:
        return None

    database_row = find_user_in_database(username.strip())
    if database_row is None:
        return None

    if not database_row["is_active"]:
        return None

    if not password_is_correct(password, database_row["password_hash"]):
        return None

    return user_to_dict(database_row)


def initialize_auth():
    """Crea la base y el administrador inicial si todavía no existen."""
    initialize_database()
    admin = get_user_by_username(DEFAULT_ADMIN_USERNAME)

    if admin is None:
        create_user(
            DEFAULT_ADMIN_USERNAME,
            DEFAULT_ADMIN_PASSWORD,
            DEFAULT_ADMIN_FULL_NAME,
            role="admin",
        )
