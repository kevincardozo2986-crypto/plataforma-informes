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
    cleaned = INVALID_WINDOWS_CHARS.sub("-", str(value or "").strip())
    cleaned = re.sub(r"\s+", " ", cleaned).rstrip(". ")
    if not cleaned:
        raise ValueError("El nombre no puede estar vacío.")
    if cleaned.upper() in RESERVED_WINDOWS_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned.upper() if uppercase else cleaned


def build_report_directory(base_directory, period, level, modality, program):
    base = Path(base_directory).expanduser()
    if not str(base_directory).strip():
        raise ValueError("Selecciona una carpeta base.")
    if level not in VALID_LEVELS:
        raise ValueError("El nivel académico no es válido.")
    if modality not in VALID_MODALITIES:
        raise ValueError("La modalidad no es válida.")
    safe_period = sanitize_name(period)
    safe_program = sanitize_name(program, uppercase=True)
    category = f"{sanitize_name(level)}_{sanitize_name(modality)}"
    return base / f"INFORMES USO PLATAFORMA {safe_period}" / category / safe_program


def create_report_directory(*args, **kwargs):
    directory = build_report_directory(*args, **kwargs)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def build_excel_path(directory, period):
    return Path(directory) / f"Informe_{sanitize_name(period)}.xlsx"


def build_word_path(directory, period, program_code):
    code = sanitize_name(program_code, uppercase=True).replace(" ", "_")
    return Path(directory) / f"Informe_{sanitize_name(period)}_{code}.docx"


def build_pdf_path(directory, period, program_code):
    code = sanitize_name(program_code, uppercase=True).replace(" ", "_")
    return Path(directory) / f"Informe_{sanitize_name(period)}_{code}.pdf"


def prepare_report_paths(base_directory, period, level, modality, program, source_csv, program_code=None):
    directory = build_report_directory(base_directory, period, level, modality, program)
    csv_name = sanitize_name(Path(source_csv).name)
    return ReportPaths(
        directory=directory,
        source_csv=directory / csv_name,
        excel=build_excel_path(directory, period),
        word=build_word_path(directory, period, program_code) if program_code else None,
        pdf=build_pdf_path(directory, period, program_code) if program_code else None,
    )


def copy_source_csv(source_csv, destination, overwrite=False, progress_callback=None):
    source = Path(source_csv)
    target = Path(destination)
    if not source.is_file():
        raise FileNotFoundError("El CSV seleccionado ya no existe.")
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() == target.resolve():
        if progress_callback:
            progress_callback(100)
        return target
    if target.exists() and not overwrite:
        raise FileExistsError(str(target))
    total_size = max(source.stat().st_size, 1)
    copied = 0
    with source.open("rb") as input_file, target.open("wb") as output_file:
        while block := input_file.read(4 * 1024 * 1024):
            output_file.write(block)
            copied += len(block)
            if progress_callback:
                progress_callback(min(45 + int(copied * 55 / total_size), 99))
    shutil.copystat(source, target)
    if progress_callback:
        progress_callback(100)
    return target
