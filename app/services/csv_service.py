"""Lectura y preparación de archivos CSV exportados desde Moodle."""

from pathlib import Path
import csv

import pandas as pd


class CSVValidationError(ValueError):
    pass


def detect_csv_format(path):
    """Detecta codificación y separador leyendo solo una pequeña muestra."""
    csv_path = Path(path)
    if not csv_path.is_file() or csv_path.suffix.lower() != ".csv":
        raise CSVValidationError("Selecciona un archivo CSV válido.")
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with csv_path.open("r", encoding=encoding, newline="") as source:
                sample = source.read(64 * 1024)
            try:
                delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
            except csv.Error:
                delimiter = ","
            return encoding, delimiter
        except UnicodeDecodeError:
            continue
    raise CSVValidationError("No fue posible detectar el formato del CSV.")


def iter_csv_chunks(path, chunksize=25_000, prepare=False):
    """Entrega bloques para evitar cargar archivos grandes completos en memoria."""
    encoding, delimiter = detect_csv_format(path)
    try:
        chunks = pd.read_csv(
            path,
            sep=delimiter,
            encoding=encoding,
            chunksize=chunksize,
            dtype_backend="numpy_nullable",
        )
        for chunk in chunks:
            chunk.columns = [str(column).strip() for column in chunk.columns]
            yield prepare_original_data(chunk) if prepare else chunk
    except pd.errors.ParserError as error:
        raise CSVValidationError(f"No fue posible interpretar el CSV: {error}") from error


def inspect_csv_structure(path):
    """Valida encabezados leyendo solo una muestra, sin recorrer el archivo completo."""
    encoding, delimiter = detect_csv_format(path)
    try:
        sample = pd.read_csv(
            path,
            sep=delimiter,
            encoding=encoding,
            nrows=5,
            dtype_backend="numpy_nullable",
        )
    except pd.errors.ParserError as error:
        raise CSVValidationError(f"No fue posible interpretar el CSV: {error}") from error
    columns = [str(column).strip() for column in sample.columns]
    if not columns:
        raise CSVValidationError("El archivo no contiene columnas.")
    if "fechaunix" not in {column.casefold() for column in columns}:
        raise CSVValidationError("El CSV no contiene la columna requerida 'FechaUnix'.")
    return columns


def estimate_csv_rows(path):
    """Cuenta saltos de línea rápidamente para calcular progreso aproximado."""
    line_count = 0
    with Path(path).open("rb") as source:
        while block := source.read(4 * 1024 * 1024):
            line_count += block.count(b"\n")
    return max(line_count - 1, 1)


def read_csv_file(path):
    """Lee un CSV detectando separador y probando codificaciones comunes."""
    csv_path = Path(path)
    if not csv_path.is_file() or csv_path.suffix.lower() != ".csv":
        raise CSVValidationError("Selecciona un archivo CSV válido.")
    encoding, delimiter = detect_csv_format(csv_path)
    try:
        frame = pd.read_csv(
            csv_path,
            sep=delimiter,
            encoding=encoding,
            dtype_backend="numpy_nullable",
        )
    except pd.errors.ParserError as error:
        raise CSVValidationError(f"No fue posible interpretar el CSV: {error}") from error
    if not len(frame.columns):
        raise CSVValidationError("El archivo no contiene columnas.")
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def derive_date_columns_from_unix(frame, timezone="America/Bogota"):
    """Agrega Fecha, Mes y Dia a partir de la columna FechaUnix de Moodle."""
    prepared = frame.copy()
    normalized = {str(column).strip().casefold(): column for column in prepared.columns}
    unix_column = normalized.get("fechaunix")
    if unix_column is None:
        raise CSVValidationError("El CSV no contiene la columna requerida 'FechaUnix'.")

    numeric_values = pd.to_numeric(prepared[unix_column], errors="coerce")
    valid_values = numeric_values.dropna()
    if valid_values.empty:
        raise CSVValidationError("La columna 'FechaUnix' no contiene valores Unix válidos.")

    typical_value = valid_values.abs().median()
    unit = "ms" if typical_value >= 100_000_000_000 else "s"
    dates = pd.to_datetime(numeric_values, unit=unit, errors="coerce", utc=True)
    local_dates = dates.dt.tz_convert(timezone).dt.tz_localize(None)

    derived_names = {"fecha", "mes", "dia", "día"}
    existing_derived = [
        column
        for column in prepared.columns
        if str(column).strip().casefold() in derived_names and column != unix_column
    ]
    if existing_derived:
        prepared = prepared.drop(columns=existing_derived)

    insert_at = prepared.columns.get_loc(unix_column) + 1
    prepared.insert(insert_at, "Fecha", local_dates.dt.date)
    prepared.insert(insert_at + 1, "Mes", local_dates.dt.month.astype("Int64"))
    prepared.insert(insert_at + 2, "Dia", local_dates.dt.day.astype("Int64"))
    return prepared


def prepare_original_data(frame):
    """Alias compatible para la preparación actual de la hoja Original."""
    return derive_date_columns_from_unix(frame)
