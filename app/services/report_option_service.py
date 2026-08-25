"""Consulta y administración de las opciones para crear informes."""

import re
import sqlite3

from app.database.database import get_connection


CATEGORIAS_VALIDAS = {"period", "level", "modality", "program"}


def list_report_options(categoria):
    """Devuelve las opciones disponibles de una categoría."""
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("La categoría de opciones no es válida.")

    with get_connection() as conexion:
        filas = conexion.execute(
            """
            SELECT value
            FROM report_options
            WHERE category = ?
            ORDER BY id
            """,
            (categoria,),
        ).fetchall()
    return [fila["value"] for fila in filas]


def add_report_option(usuario_actual, categoria, valor):
    """Agrega una opción; solamente un administrador puede hacerlo."""
    if not usuario_actual or usuario_actual.get("role") != "admin":
        raise PermissionError("Solo un administrador puede agregar opciones.")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("La categoría de opciones no es válida.")

    valor_limpio = " ".join(str(valor or "").split())
    if not valor_limpio:
        raise ValueError("La opción no puede estar vacía.")
    if len(valor_limpio) > 100:
        raise ValueError("La opción no puede superar 100 caracteres.")
    if categoria == "period" and not re.fullmatch(r"\d{4}-[12]", valor_limpio):
        raise ValueError(
            "El periodo debe tener el formato AAAA-S, por ejemplo 2026-1. "
            "El semestre solo puede ser 1 o 2."
        )

    try:
        with get_connection() as conexion:
            conexion.execute(
                "INSERT INTO report_options (category, value) VALUES (?, ?)",
                (categoria, valor_limpio),
            )
    except sqlite3.IntegrityError as error:
        raise ValueError("Esa opción ya existe.") from error

    return valor_limpio


def delete_report_option(usuario_actual, categoria, valor):
    """Elimina una opción existente sin permitir que la lista quede vacía."""
    if not usuario_actual or usuario_actual.get("role") != "admin":
        raise PermissionError("Solo un administrador puede eliminar opciones.")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("La categoría de opciones no es válida.")

    with get_connection() as conexion:
        cantidad_opciones = conexion.execute(
            "SELECT COUNT(*) FROM report_options WHERE category = ?",
            (categoria,),
        ).fetchone()[0]
        if cantidad_opciones <= 1:
            raise ValueError("Debe quedar al menos una opción en la lista.")

        cursor = conexion.execute(
            "DELETE FROM report_options WHERE category = ? AND value = ?",
            (categoria, valor),
        )
        if cursor.rowcount == 0:
            raise ValueError("La opción seleccionada ya no existe.")


def update_report_option(usuario_actual, categoria, valor_actual, valor_nuevo):
    """Cambia el texto de una opción existente."""
    if not usuario_actual or usuario_actual.get("role") != "admin":
        raise PermissionError("Solo un administrador puede editar opciones.")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValueError("La categoría de opciones no es válida.")

    valor_limpio = " ".join(str(valor_nuevo or "").split())
    if not valor_limpio:
        raise ValueError("La opción no puede estar vacía.")
    if len(valor_limpio) > 100:
        raise ValueError("La opción no puede superar 100 caracteres.")
    if categoria == "period" and not re.fullmatch(r"\d{4}-[12]", valor_limpio):
        raise ValueError(
            "El periodo debe tener el formato AAAA-S, por ejemplo 2026-1. "
            "El semestre solo puede ser 1 o 2."
        )

    try:
        with get_connection() as conexion:
            cursor = conexion.execute(
                """
                UPDATE report_options
                SET value = ?
                WHERE category = ? AND value = ?
                """,
                (valor_limpio, categoria, valor_actual),
            )
            if cursor.rowcount == 0:
                raise ValueError("La opción seleccionada ya no existe.")
    except sqlite3.IntegrityError as error:
        raise ValueError("Esa opción ya existe.") from error
    return valor_limpio
