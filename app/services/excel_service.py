"""Creación progresiva y consulta del libro Excel de trabajo."""

import re
import shutil
import tempfile
from collections import defaultdict
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

MESES_ABREVIADOS = {
    1: "ENE",
    2: "FEB",
    3: "MAR",
    4: "ABR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DIC",
}


class ExcelProcess:
    """Mantiene un único archivo temporal durante todo el proceso."""

    def __init__(self):
        self._temporary_directory = tempfile.TemporaryDirectory(prefix="plataforma_informes_")
        self.path = Path(self._temporary_directory.name) / "informe_en_proceso.xlsx"
        self._row_counts = {}
        self._teacher_summary_cache = None

    @property
    def exists(self):
        return self.path.is_file()

    def create_original(self, datos):
        self._write_original(datos)

    def create_original_from_chunks(self, chunks, total_rows=None, progress_callback=None):
        """Crea Original con escritura rápida y memoria constante."""
        libro_excel = xlsxwriter.Workbook(
            self.path,
            {
                "constant_memory": True,
                "default_date_format": "dd/mm/yyyy",
                "strings_to_urls": False,
            },
        )
        hoja_original = libro_excel.add_worksheet("Original")
        formato_encabezado = libro_excel.add_format(
            {"bold": True, "font_color": "#FFFFFF", "bg_color": "#0A3A6B", "align": "center"}
        )
        cantidad_filas = 0
        cantidad_columnas = 0
        indices_docentes = None
        dias_por_mes_cache = defaultdict(lambda: defaultdict(set))
        dias_periodo_cache = defaultdict(set)
        try:
            for bloque_datos in chunks:
                if cantidad_columnas == 0:
                    encabezados = [str(valor) for valor in bloque_datos.columns]
                    cantidad_columnas = len(encabezados)
                    columnas_normalizadas = {
                        encabezado.strip().casefold(): indice
                        for indice, encabezado in enumerate(encabezados)
                    }
                    requeridas_docentes = ("rol", "curso", "usuario", "mes", "dia")
                    if all(
                        nombre in columnas_normalizadas
                        for nombre in requeridas_docentes
                    ):
                        indices_docentes = {
                            nombre: columnas_normalizadas[nombre]
                            for nombre in requeridas_docentes
                        }
                    hoja_original.write_row(0, 0, encabezados, formato_encabezado)
                    for indice, encabezado in enumerate(encabezados):
                        hoja_original.set_column(indice, indice, min(max(len(encabezado) + 2, 11), 30))
                for valores_fila in bloque_datos.itertuples(index=False, name=None):
                    hoja_original.write_row(
                        cantidad_filas + 1,
                        0,
                        [self._excel_value(valor) for valor in valores_fila],
                    )
                    if indices_docentes:
                        self._acumular_actividad_docente(
                            valores_fila,
                            indices_docentes,
                            dias_por_mes_cache,
                            dias_periodo_cache,
                        )
                    cantidad_filas += 1
                if progress_callback and total_rows:
                    progress_callback(min(int(cantidad_filas * 96 / total_rows) + 2, 98))
            if cantidad_columnas == 0:
                raise ValueError("El CSV no contiene columnas ni registros legibles.")
            hoja_original.freeze_panes(1, 0)
            hoja_original.autofilter(0, 0, cantidad_filas, cantidad_columnas - 1)
        finally:
            libro_excel.close()
        self._row_counts["Original"] = cantidad_filas
        self._teacher_summary_cache = (
            (dias_por_mes_cache, dias_periodo_cache)
            if dias_por_mes_cache
            else None
        )
        if progress_callback:
            progress_callback(100)
        return cantidad_filas, cantidad_columnas

    @staticmethod
    def _acumular_actividad_docente(
        valores_fila, indices, dias_por_mes, dias_periodo
    ):
        """Acumula solo los datos necesarios mientras Original ya se está escribiendo."""
        rol = valores_fila[indices["rol"]]
        if str(rol or "").strip().casefold() != "editingteacher":
            return
        curso = str(valores_fila[indices["curso"]] or "").strip()
        docente = str(valores_fila[indices["usuario"]] or "").strip()
        try:
            mes = int(float(valores_fila[indices["mes"]]))
            dia = int(float(valores_fila[indices["dia"]]))
        except (TypeError, ValueError):
            return
        if not curso or not docente or not 1 <= mes <= 12 or not 1 <= dia <= 31:
            return
        clave = (curso, docente)
        dias_por_mes[clave][mes].add(dia)
        dias_periodo[clave].add(dia)

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

    def update_original(self, datos):
        self._write_original(datos)

    def _write_original(self, datos):
        modo_escritura = "a" if self.exists else "w"
        opciones_escritura = {"mode": modo_escritura, "engine": "openpyxl"}
        if modo_escritura == "a":
            opciones_escritura["if_sheet_exists"] = "replace"
        with pd.ExcelWriter(self.path, **opciones_escritura) as escritor:
            datos.to_excel(escritor, sheet_name="Original", index=False)
        if modo_escritura == "a":
            libro_excel = load_workbook(self.path)
            if "Tabla Dinamica Docentes" in libro_excel.sheetnames:
                libro_excel.remove(libro_excel["Tabla Dinamica Docentes"])
                libro_excel.save(self.path)
        self._row_counts["Original"] = len(datos)
        self._row_counts.pop("Tabla Dinamica Docentes", None)
        self._format_sheet("Original")

    def _format_sheet(self, sheet_name):
        libro_excel = load_workbook(self.path)
        hoja = libro_excel[sheet_name]
        relleno_encabezado = PatternFill("solid", fgColor="0A3A6B")
        for celda in hoja[1]:
            celda.fill = relleno_encabezado
            celda.font = Font(color="FFFFFF", bold=True)
            celda.alignment = Alignment(horizontal="center")
        hoja.freeze_panes = "A2"
        hoja.auto_filter.ref = hoja.dimensions
        for indice, columna in enumerate(hoja.iter_cols(min_row=1, max_row=min(hoja.max_row, 200)), 1):
            ancho = max((len(str(celda.value or "")) for celda in columna), default=8)
            hoja.column_dimensions[get_column_letter(indice)].width = min(max(ancho + 2, 11), 38)
        libro_excel.save(self.path)

    def crear_tabla_docentes(self, progress_callback=None):
        """Crea la segunda hoja con días distintos por curso, docente y mes."""
        if not self.exists:
            raise FileNotFoundError("Primero debes crear la hoja Original.")
        if progress_callback:
            progress_callback(5)

        if self._teacher_summary_cache:
            dias_por_mes, dias_periodo = self._teacher_summary_cache
            if progress_callback:
                progress_callback(58)
            return self._guardar_tabla_docentes(
                dias_por_mes, dias_periodo, progress_callback
            )

        libro_lectura = load_workbook(self.path, read_only=True, data_only=True)
        hoja_original = libro_lectura["Original"]
        filas_originales = hoja_original.iter_rows(values_only=True)
        encabezados_originales = next(filas_originales, None)
        if not encabezados_originales:
            libro_lectura.close()
            raise ValueError("La hoja Original está vacía.")

        columnas = {
            str(nombre).strip().casefold(): indice
            for indice, nombre in enumerate(encabezados_originales)
        }
        requeridas = ("rol", "curso", "usuario", "mes", "dia")
        faltantes = [nombre for nombre in requeridas if nombre not in columnas]
        if faltantes:
            libro_lectura.close()
            raise ValueError(
                "La hoja Original no contiene las columnas requeridas: "
                + ", ".join(faltantes)
            )

        dias_por_mes = defaultdict(lambda: defaultdict(set))
        dias_periodo = defaultdict(set)
        total_filas_original = max((hoja_original.max_row or 1) - 1, 1)
        try:
            for numero_fila, fila in enumerate(filas_originales, 1):
                rol = fila[columnas["rol"]]
                if str(rol or "").strip().casefold() != "editingteacher":
                    if progress_callback and numero_fila % 5_000 == 0:
                        progress_callback(
                            min(5 + int(numero_fila * 50 / total_filas_original), 55)
                        )
                    continue

                curso = str(fila[columnas["curso"]] or "").strip()
                docente = str(fila[columnas["usuario"]] or "").strip()
                try:
                    mes = int(float(fila[columnas["mes"]]))
                    dia = int(float(fila[columnas["dia"]]))
                except (TypeError, ValueError):
                    continue
                if not curso or not docente or not 1 <= mes <= 12 or not 1 <= dia <= 31:
                    continue

                clave = (curso, docente)
                dias_por_mes[clave][mes].add(dia)
                dias_periodo[clave].add(dia)
                if progress_callback and numero_fila % 5_000 == 0:
                    progress_callback(
                        min(5 + int(numero_fila * 50 / total_filas_original), 55)
                    )
        finally:
            libro_lectura.close()

        if not dias_por_mes:
            raise ValueError(
                "No se encontraron registros con rol 'editingteacher' en Original."
            )
        if progress_callback:
            progress_callback(58)

        meses_encontrados = sorted(
            {mes for meses in dias_por_mes.values() for mes in meses}
        )
        encabezados_resumen = [
            "CURSO",
            "DOCENTE",
            *(MESES_ABREVIADOS[mes] for mes in meses_encontrados),
            "Total general",
        ]
        filas_resumen = []
        for clave in sorted(
            dias_por_mes,
            key=lambda valores: (valores[0].casefold(), valores[1].casefold()),
        ):
            curso, docente = clave
            filas_resumen.append(
                [
                    curso,
                    docente,
                    *(len(dias_por_mes[clave][mes]) for mes in meses_encontrados),
                    len(dias_periodo[clave]),
                ]
            )
        if progress_callback:
            progress_callback(65)

        if progress_callback:
            progress_callback(70)
        libro_excel = load_workbook(self.path)
        if progress_callback:
            progress_callback(82)
        nombre_hoja = "Tabla Dinamica Docentes"
        if nombre_hoja in libro_excel.sheetnames:
            libro_excel.remove(libro_excel[nombre_hoja])
        hoja = libro_excel.create_sheet(nombre_hoja)
        hoja.append(encabezados_resumen)
        for fila in filas_resumen:
            hoja.append([self._excel_value(valor) for valor in fila])

        relleno_encabezado = PatternFill("solid", fgColor="0A3A6B")
        for celda in hoja[1]:
            celda.fill = relleno_encabezado
            celda.font = Font(color="FFFFFF", bold=True)
            celda.alignment = Alignment(horizontal="center", vertical="center")
        for fila in hoja.iter_rows(min_row=2):
            fila[0].alignment = Alignment(horizontal="left", vertical="center")
            fila[1].alignment = Alignment(horizontal="left", vertical="center")
            for celda in fila[2:]:
                celda.alignment = Alignment(horizontal="center", vertical="center")
        hoja.column_dimensions["A"].width = 42
        hoja.column_dimensions["B"].width = 34
        for indice in range(3, hoja.max_column + 1):
            hoja.column_dimensions[get_column_letter(indice)].width = 14
        hoja.freeze_panes = "C2"
        hoja.auto_filter.ref = hoja.dimensions
        if progress_callback:
            progress_callback(90)
        libro_excel.save(self.path)

        cantidad_filas = len(filas_resumen)
        self._row_counts[nombre_hoja] = cantidad_filas
        if progress_callback:
            progress_callback(100)
        return cantidad_filas, [MESES_ABREVIADOS[mes] for mes in meses_encontrados]

    def _guardar_tabla_docentes(
        self, dias_por_mes, dias_periodo, progress_callback=None
    ):
        """Escribe la tabla pequeña usando el resumen acumulado durante Original."""
        meses_encontrados = sorted(
            {mes for meses in dias_por_mes.values() for mes in meses}
        )
        encabezados = [
            "CURSO",
            "DOCENTE",
            *(MESES_ABREVIADOS[mes] for mes in meses_encontrados),
            "Total general",
        ]
        filas = []
        for clave in sorted(
            dias_por_mes,
            key=lambda valores: (valores[0].casefold(), valores[1].casefold()),
        ):
            curso, docente = clave
            filas.append(
                [
                    curso,
                    docente,
                    *(len(dias_por_mes[clave][mes]) for mes in meses_encontrados),
                    len(dias_periodo[clave]),
                ]
            )
        nombre_hoja = "Tabla Dinamica Docentes"
        ruta_nueva = self.path.with_name("informe_actualizado.xlsx")
        libro_lectura = load_workbook(self.path, read_only=True, data_only=False)
        hoja_lectura = libro_lectura["Original"]
        total_original = max(hoja_lectura.max_row or 1, 1)
        libro_salida = xlsxwriter.Workbook(
            ruta_nueva,
            {
                "constant_memory": True,
                "default_date_format": "dd/mm/yyyy",
                "strings_to_urls": False,
            },
        )
        formato_encabezado = libro_salida.add_format(
            {
                "bold": True,
                "font_color": "#FFFFFF",
                "bg_color": "#0A3A6B",
                "align": "center",
                "valign": "vcenter",
            }
        )
        formato_centrado = libro_salida.add_format(
            {"align": "center", "valign": "vcenter"}
        )
        try:
            original_salida = libro_salida.add_worksheet("Original")
            for indice_fila, valores in enumerate(
                hoja_lectura.iter_rows(values_only=True)
            ):
                formato = formato_encabezado if indice_fila == 0 else None
                original_salida.write_row(
                    indice_fila,
                    0,
                    [self._excel_value(valor) for valor in valores],
                    formato,
                )
                if indice_fila == 0:
                    for indice_columna, encabezado in enumerate(valores):
                        ancho = min(max(len(str(encabezado or "")) + 2, 11), 30)
                        original_salida.set_column(
                            indice_columna, indice_columna, ancho
                        )
                if progress_callback and indice_fila % 5_000 == 0:
                    progress_callback(
                        min(60 + int(indice_fila * 28 / total_original), 88)
                    )
            original_salida.freeze_panes(1, 0)
            if hoja_lectura.max_column:
                original_salida.autofilter(
                    0, 0, max(total_original - 1, 0), hoja_lectura.max_column - 1
                )

            tabla_salida = libro_salida.add_worksheet(nombre_hoja)
            tabla_salida.write_row(0, 0, encabezados, formato_encabezado)
            for indice_fila, fila in enumerate(filas, 1):
                tabla_salida.write(indice_fila, 0, fila[0])
                tabla_salida.write(indice_fila, 1, fila[1])
                tabla_salida.write_row(
                    indice_fila, 2, fila[2:], formato_centrado
                )
            tabla_salida.set_column(0, 0, 42)
            tabla_salida.set_column(1, 1, 34)
            tabla_salida.set_column(2, len(encabezados) - 1, 14)
            tabla_salida.freeze_panes(1, 2)
            tabla_salida.autofilter(0, 0, len(filas), len(encabezados) - 1)
            if progress_callback:
                progress_callback(92)
        finally:
            libro_lectura.close()
            libro_salida.close()

        ruta_nueva.replace(self.path)

        cantidad_filas = len(filas)
        self._row_counts[nombre_hoja] = cantidad_filas
        if progress_callback:
            progress_callback(100)
        return cantidad_filas, [MESES_ABREVIADOS[mes] for mes in meses_encontrados]

    def sheet_names(self):
        if not self.exists:
            return []
        libro_excel = load_workbook(self.path, read_only=True)
        nombres_hojas = list(libro_excel.sheetnames)
        libro_excel.close()
        return nombres_hojas

    def preview_sheet(self, sheet_name, limit=200):
        libro_excel = load_workbook(self.path, read_only=True, data_only=True)
        try:
            hoja = libro_excel[sheet_name]
            total_filas = self._row_counts.get(sheet_name)
            if total_filas is None:
                total_filas = max((hoja.max_row or 1) - 1, 0)
            filas = []
            for indice, fila in enumerate(hoja.iter_rows(values_only=True)):
                if indice > limit:
                    break
                filas.append(fila)
        finally:
            libro_excel.close()
        if not filas:
            return [], [], total_filas
        encabezados = [str(valor or "") for valor in filas[0]]
        return encabezados, filas[1:], total_filas

    def save_as(self, destination):
        if not self.exists:
            raise FileNotFoundError("Todavía no existe un Excel de trabajo.")
        shutil.copy2(self.path, destination)


def suggested_filename(period, program):
    periodo_seguro = re.sub(r"[^\w-]+", "_", period.strip(), flags=re.UNICODE)
    programa_seguro = re.sub(r"[^\w-]+", "_", program.strip(), flags=re.UNICODE).strip("_")
    return f"Informe_{periodo_seguro}_{programa_seguro}.xlsx"
