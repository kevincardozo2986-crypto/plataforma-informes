def user_to_dict(database_row):
    """Convierte una fila de SQLite en datos seguros para la interfaz."""
    return {
        "id": database_row["id"],
        "username": database_row["username"],
        "full_name": database_row["full_name"],
        "role": database_row["role"],
        "is_active": bool(database_row["is_active"]),
        "created_at": database_row["created_at"],
    }
