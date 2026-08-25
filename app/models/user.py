def user_to_dict(fila_base_datos):
    """Convierte una fila de SQLite en datos seguros para la interfaz."""
    return {
        "id": fila_base_datos["id"],
        "username": fila_base_datos["username"],
        "full_name": fila_base_datos["full_name"],
        "role": fila_base_datos["role"],
        "is_active": bool(fila_base_datos["is_active"]),
        "created_at": fila_base_datos["created_at"],
    }
