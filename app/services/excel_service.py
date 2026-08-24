"""Creación progresiva y consulta del libro Excel de trabajo."""

import re
import shutil
import tempfile
from pathlib import Path

import pandas as pd
import xlsxwriter
from openpyxl import load_workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


SHEET_NAMES = (
    "Original",
    "Tabla Dinamica Docentes",
    "Docentes",
    "Docentes DG",
    "Tabla Dinamica Estudiantes",
    "Estudiantes",
    "Estudiantes DG",
    "Estudiantes DG2",
    "Tabla Dinamica Actividades",
    "Diseño de Cursos",
)


class ExcelProcess:
    """Mantiene un único archivo temporal durante todo el proceso."""

    def __init__(self):
        self._temporary_directory = tempfile.TemporaryDirectory(prefix="plataforma_informes_")
        self.path = Path(self._temporary_directory.name) / "informe_en_proceso.xlsx"
        self._row_counts = {}

    @property
    def exists(self):
        return self.path.is_file()

    def create_original(self, frame):
        self._write_original(frame)

    def create_original_from_chunks(self, chunks, total_rows=None, progress_callback=None):
        """Crea Original con escritura rápida y memoria constante."""
        workbook = xlsxwriter.Workbook(
            self.path,
            {
                "constant_memory": True,
                "default_date_format": "dd/mm/yyyy",
                "strings_to_urls": False,
            },
        )
        sheet = workbook.add_worksheet("Original")
        header_format = workbook.add_format(
            {"bold": True, "font_color": "#FFFFFF", "bg_color": "#0A3A6B", "align": "center"}
        )
        row_count = 0
        column_count = 0
        try:
            for chunk in chunks:
                if column_count == 0:
                    headers = [str(value) for value in chunk.columns]
                    column_count = len(headers)
                    sheet.write_row(0, 0, headers, header_format)
                    for index, header in enumerate(headers):
                        sheet.set_column(index, index, min(max(len(header) + 2, 11), 30))
                for values in chunk.itertuples(index=False, name=None):
                    sheet.write_row(
                        row_count + 1,
                        0,
                        [self._excel_value(value) for value in values],
                    )
                    row_count += 1
                if progress_callback and total_rows:
                    progress_callback(min(int(row_count * 96 / total_rows) + 2, 98))
            if column_count == 0:
                raise ValueError("El CSV no contiene columnas ni registros legibles.")
            sheet.freeze_panes(1, 0)
            sheet.autofilter(0, 0, row_count, column_count - 1)
        finally:
            workbook.close()
        self._row_counts["Original"] = row_count
        if progress_callback:
            progress_callback(100)
        return row_count, column_count

    @staticmethod
    def _excel_value(value):
        if pd.isna(value):
            return None
        if hasattr(value, "to_pydatetime"):
            value = value.to_pydatetime()
        elif hasattr(value, "item"):
            value = value.item()
        if isinstance(value, str):
            return ILLEGAL_CHARACTERS_RE.sub("", value)
        return value

    def update_original(self, frame):
        self._write_original(frame)

    def _write_original(self, frame):
        mode = "a" if self.exists else "w"
        options = {"mode": mode, "engine": "openpyxl"}
        if mode == "a":
            options["if_sheet_exists"] = "replace"
        with pd.ExcelWriter(self.path, **options) as writer:
            frame.to_excel(writer, sheet_name="Original", index=False)
        self._row_counts["Original"] = len(frame)
        self._format_sheet("Original")

    def _format_sheet(self, sheet_name):
        workbook = load_workbook(self.path)
        sheet = workbook[sheet_name]
        header_fill = PatternFill("solid", fgColor="0A3A6B")
        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = Font(color="FFFFFF", bold=True)
            cell.alignment = Alignment(horizontal="center")
        sheet.freeze_panes = "A2"
        sheet.auto_filter.ref = sheet.dimensions
        for index, column in enumerate(sheet.iter_cols(min_row=1, max_row=min(sheet.max_row, 200)), 1):
            width = max((len(str(cell.value or "")) for cell in column), default=8)
            sheet.column_dimensions[get_column_letter(index)].width = min(max(width + 2, 11), 38)
        workbook.save(self.path)

    def sheet_names(self):
        if not self.exists:
            return []
        workbook = load_workbook(self.path, read_only=True)
        names = list(workbook.sheetnames)
        workbook.close()
        return names

    def preview_sheet(self, sheet_name, limit=200):
        workbook = load_workbook(self.path, read_only=True, data_only=True)
        try:
            sheet = workbook[sheet_name]
            total_rows = self._row_counts.get(sheet_name)
            if total_rows is None:
                total_rows = max((sheet.max_row or 1) - 1, 0)
            values = []
            for index, row in enumerate(sheet.iter_rows(values_only=True)):
                if index > limit:
                    break
                values.append(row)
        finally:
            workbook.close()
        if not values:
            return [], [], total_rows
        headers = [str(value or "") for value in values[0]]
        return headers, values[1:], total_rows

    def save_as(self, destination):
        if not self.exists:
            raise FileNotFoundError("Todavía no existe un Excel de trabajo.")
        shutil.copy2(self.path, destination)


def suggested_filename(period, program):
    safe_period = re.sub(r"[^\w-]+", "_", period.strip(), flags=re.UNICODE)
    safe_program = re.sub(r"[^\w-]+", "_", program.strip(), flags=re.UNICODE).strip("_")
    return f"Informe_{safe_period}_{safe_program}.xlsx"
