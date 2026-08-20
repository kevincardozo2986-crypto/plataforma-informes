"""Acceso a la base de datos de la aplicación."""

from .database import get_connection, initialize_database

__all__ = ["get_connection", "initialize_database"]
