"""Construcción del carpetado institucional de informes."""

import re
import shutil
from dataclasses import dataclass
from pathlib import Path


INVALID_WINDOWS_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RESERVED_WINDOWS_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
VALID_LEVELS = {"Pregrado", "Posgrado"}
VALID_MODALITIES = {"Presencial", "Virtual", "Presencial-Virtual"}


@dataclass(frozen=True)
class ReportPaths:
    directory: Path
    source_csv: Path
    excel: Path
    word: Path | None
    pdf: Path | None


def sanitize_name(value, uppercase=False):
    """Conserva nombres legibles y elimina caracteres inválidos en Windows."""
    nombre_limpio = INVALID_WINDOWS_CHARS.sub("-", str(value or "").strip())
    nombre_limpio = re.sub(r"\s+", " ", nombre_limpio).rstrip(". ")
    if not nombre_limpio:
        raise ValueError("El nombre no puede estar vacío.")
    if nombre_limpio.upper() in RESERVED_WINDOWS_NAMES:
        nombre_limpio = f"_{nombre_limpio}"
    return nombre_limpio.upper() if uppercase else nombre_limpio


def build_report_directory(base_directory, period, level, modality, program):
    carpeta_base = Path(base_directory).expanduser()
    if not str(base_directory).strip():
        raise ValueError("Selecciona una carpeta base.")
    if level not in VALID_LEVELS:
        raise ValueError("El nivel académico no es válido.")
    if modality not in VALID_MODALITIES:
        raise ValueError("La modalidad no es válida.")
    periodo_seguro = sanitize_name(period)
    programa_seguro = sanitize_name(program, uppercase=True)
    categoria = f"{sanitize_name(level)}_{sanitize_name(modality)}"
    return carpeta_base / f"INFORMES USO PLATAFORMA {periodo_seguro}" / categoria / programa_seguro


def create_report_directory(*args, **kwargs):
    carpeta_informe = build_report_directory(*args, **kwargs)
    carpeta_informe.mkdir(parents=True, exist_ok=True)
    return carpeta_informe


def build_excel_path(directory, period):
    return Path(directory) / f"Informe_{sanitize_name(period)}.xlsx"


def build_word_path(directory, period, program_code):
    codigo_programa = sanitize_name(program_code, uppercase=True).replace(" ", "_")
    return Path(directory) / f"Informe_{sanitize_name(period)}_{codigo_programa}.docx"


def build_pdf_path(directory, period, program_code):
    codigo_programa = sanitize_name(program_code, uppercase=True).replace(" ", "_")
    return Path(directory) / f"Informe_{sanitize_name(period)}_{codigo_programa}.pdf"


def prepare_report_paths(base_directory, period, level, modality, program, source_csv, program_code=None):
    carpeta_informe = build_report_directory(base_directory, period, level, modality, program)
    nombre_csv = sanitize_name(Path(source_csv).name)
    return ReportPaths(
        directory=carpeta_informe,
        source_csv=carpeta_informe / nombre_csv,
        excel=build_excel_path(carpeta_informe, period),
        word=build_word_path(carpeta_informe, period, program_code) if program_code else None,
        pdf=build_pdf_path(carpeta_informe, period, program_code) if program_code else None,
    )


def copy_source_csv(source_csv, destination, overwrite=False, progress_callback=None):
    archivo_origen = Path(source_csv)
    archivo_destino = Path(destination)
    if not archivo_origen.is_file():
        raise FileNotFoundError("El CSV seleccionado ya no existe.")
    archivo_destino.parent.mkdir(parents=True, exist_ok=True)
    if archivo_origen.resolve() == archivo_destino.resolve():
        if progress_callback:
            progress_callback(100)
        return archivo_destino
    if archivo_destino.exists() and not overwrite:
        raise FileExistsError(str(archivo_destino))
    tamano_total = max(archivo_origen.stat().st_size, 1)
    bytes_copiados = 0
    with archivo_origen.open("rb") as entrada, archivo_destino.open("wb") as salida:
        while bloque := entrada.read(4 * 1024 * 1024):
            salida.write(bloque)
            bytes_copiados += len(bloque)
            if progress_callback:
                progress_callback(min(45 + int(bytes_copiados * 55 / tamano_total), 99))
    shutil.copystat(archivo_origen, archivo_destino)
    if progress_callback:
        progress_callback(100)
    return archivo_destino
