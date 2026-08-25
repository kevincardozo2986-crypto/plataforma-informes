"""Lectura y preparación de archivos CSV exportados desde Moodle."""

from pathlib import Path
import csv

import pandas as pd


class CSVValidationError(ValueError):
    pass


def detect_csv_format(ruta_archivo):
    """Detecta codificación y separador leyendo solo una pequeña muestra."""
    ruta_csv = Path(ruta_archivo)
    if not ruta_csv.is_file() or ruta_csv.suffix.lower() != ".csv":
        raise CSVValidationError("Selecciona un archivo CSV válido.")
    for codificacion in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            with ruta_csv.open("r", encoding=codificacion, newline="") as archivo:
                muestra = archivo.read(64 * 1024)
            try:
                separador = csv.Sniffer().sniff(muestra, delimiters=",;\t|").delimiter
            except csv.Error:
                separador = ","
            return codificacion, separador
        except UnicodeDecodeError:
            continue
    raise CSVValidationError("No fue posible detectar el formato del CSV.")


def iter_csv_chunks(ruta_archivo, chunksize=25_000, prepare=False):
    """Entrega bloques para evitar cargar archivos grandes completos en memoria."""
    codificacion, separador = detect_csv_format(ruta_archivo)
    try:
        bloques_csv = pd.read_csv(
            ruta_archivo,
            sep=separador,
            encoding=codificacion,
            chunksize=chunksize,
            dtype_backend="numpy_nullable",
        )
        for bloque_datos in bloques_csv:
            bloque_datos.columns = [str(columna).strip() for columna in bloque_datos.columns]
            yield prepare_original_data(bloque_datos) if prepare else bloque_datos
    except pd.errors.ParserError as error:
        raise CSVValidationError(f"No fue posible interpretar el CSV: {error}") from error


def inspect_csv_structure(ruta_archivo):
    """Valida encabezados leyendo solo una muestra, sin recorrer el archivo completo."""
    codificacion, separador = detect_csv_format(ruta_archivo)
    try:
        muestra_datos = pd.read_csv(
            ruta_archivo,
            sep=separador,
            encoding=codificacion,
            nrows=5,
            dtype_backend="numpy_nullable",
        )
    except pd.errors.ParserError as error:
        raise CSVValidationError(f"No fue posible interpretar el CSV: {error}") from error
    columnas = [str(columna).strip() for columna in muestra_datos.columns]
    if not columnas:
        raise CSVValidationError("El archivo no contiene columnas.")
    if "fechaunix" not in {columna.casefold() for columna in columnas}:
        raise CSVValidationError("El CSV no contiene la columna requerida 'FechaUnix'.")
    return columnas


def estimate_csv_rows(ruta_archivo):
    """Cuenta saltos de línea rápidamente para calcular progreso aproximado."""
    cantidad_lineas = 0
    with Path(ruta_archivo).open("rb") as archivo:
        while bloque := archivo.read(4 * 1024 * 1024):
            cantidad_lineas += bloque.count(b"\n")
    return max(cantidad_lineas - 1, 1)


def read_csv_file(ruta_archivo):
    """Lee un CSV detectando separador y probando codificaciones comunes."""
    ruta_csv = Path(ruta_archivo)
    if not ruta_csv.is_file() or ruta_csv.suffix.lower() != ".csv":
        raise CSVValidationError("Selecciona un archivo CSV válido.")
    codificacion, separador = detect_csv_format(ruta_csv)
    try:
        datos_csv = pd.read_csv(
            ruta_csv,
            sep=separador,
            encoding=codificacion,
            dtype_backend="numpy_nullable",
        )
    except pd.errors.ParserError as error:
        raise CSVValidationError(f"No fue posible interpretar el CSV: {error}") from error
    if not len(datos_csv.columns):
        raise CSVValidationError("El archivo no contiene columnas.")
    datos_csv.columns = [str(columna).strip() for columna in datos_csv.columns]
    return datos_csv


def derive_date_columns_from_unix(datos, timezone="America/Bogota"):
    """Agrega Fecha, Mes y Dia a partir de la columna FechaUnix de Moodle."""
    datos_preparados = datos.copy()
    columnas_normalizadas = {
        str(columna).strip().casefold(): columna for columna in datos_preparados.columns
    }
    columna_fecha_unix = columnas_normalizadas.get("fechaunix")
    if columna_fecha_unix is None:
        raise CSVValidationError("El CSV no contiene la columna requerida 'FechaUnix'.")

    valores_numericos = pd.to_numeric(datos_preparados[columna_fecha_unix], errors="coerce")
    valores_validos = valores_numericos.dropna()
    if valores_validos.empty:
        raise CSVValidationError("La columna 'FechaUnix' no contiene valores Unix válidos.")

    valor_representativo = valores_validos.abs().median()
    unidad_tiempo = "ms" if valor_representativo >= 100_000_000_000 else "s"
    fechas_utc = pd.to_datetime(
        valores_numericos, unit=unidad_tiempo, errors="coerce", utc=True
    )
    fechas_locales = fechas_utc.dt.tz_convert(timezone).dt.tz_localize(None)

    nombres_columnas_derivadas = {"fecha", "mes", "dia", "día"}
    columnas_derivadas_existentes = [
        columna
        for columna in datos_preparados.columns
        if str(columna).strip().casefold() in nombres_columnas_derivadas
        and columna != columna_fecha_unix
    ]
    if columnas_derivadas_existentes:
        datos_preparados = datos_preparados.drop(columns=columnas_derivadas_existentes)

    posicion_insercion = datos_preparados.columns.get_loc(columna_fecha_unix) + 1
    datos_preparados.insert(posicion_insercion, "Fecha", fechas_locales.dt.date)
    datos_preparados.insert(posicion_insercion + 1, "Mes", fechas_locales.dt.month.astype("Int64"))
    datos_preparados.insert(posicion_insercion + 2, "Dia", fechas_locales.dt.day.astype("Int64"))
    return datos_preparados


def prepare_original_data(datos):
    """Alias compatible para la preparación actual de la hoja Original."""
    return derive_date_columns_from_unix(datos)
