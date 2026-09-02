"""Generacion del informe Word institucional desde el Excel terminado."""

import re
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
from openpyxl import load_workbook


TEMPLATE_FILENAME = "PLANTILLA_INFORME.docx"


def _bundled_template_path():
    """Localiza la plantilla tanto en el proyecto como en una app empaquetada."""
    bundle_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    candidates = (
        bundle_root / "templates" / TEMPLATE_FILENAME,
        Path(sys.executable).resolve().parent / "templates" / TEMPLATE_FILENAME,
        Path(__file__).resolve().parents[2] / "templates" / TEMPLATE_FILENAME,
        Path(__file__).resolve().parents[2] / TEMPLATE_FILENAME,
    )
    return next((path for path in candidates if path.is_file()), candidates[0])


TEMPLATE_PATH = _bundled_template_path()
MONTH_NAMES = {
    "ENE": "Enero", "FEB": "Febrero", "MAR": "Marzo", "ABR": "Abril",
    "MAY": "Mayo", "JUN": "Junio", "JUL": "Julio", "AGO": "Agosto",
    "SEP": "Septiembre", "OCT": "Octubre", "NOV": "Noviembre", "DIC": "Diciembre",
}
BLUE = "#2878B5"
GOLD = "#D6A419"
NAVY = "#17365D"


def _number(value, decimals=0):
    if value in (None, ""):
        return "0"
    value = float(value)
    if decimals:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(round(value)):,}".replace(",", ".")


def _find_row(sheet, label):
    target = label.strip().casefold()
    for row in range(1, sheet.max_row + 1):
        if str(sheet.cell(row, 1).value or "").strip().casefold() == target:
            return row
    raise ValueError(f"No se encontro el bloque '{label}' en Resumen Informe.")


def _read_block(sheet, label, columns):
    row = _find_row(sheet, label) + 2
    rows = []
    while row <= sheet.max_row and sheet.cell(row, 1).value not in (None, ""):
        rows.append(tuple(sheet.cell(row, column).value for column in range(1, columns + 1)))
        row += 1
    return rows


def _extract_data(workbook_path):
    workbook = load_workbook(workbook_path, read_only=True, data_only=True)
    try:
        required = {"Resumen Informe", "Docentes DG", "Tabla Dinamica Estudiantes", "Dise\u00f1o de Cursos"}
        missing = required.difference(workbook.sheetnames)
        if missing:
            raise ValueError("El Excel no contiene las hojas requeridas: " + ", ".join(sorted(missing)))

        summary = workbook["Resumen Informe"]
        indicators = _read_block(summary, "Indicadores principales", 3)
        monthly = _read_block(summary, "Actividad mensual", 4)
        courses = _read_block(summary, "Cursos destacados", 4)
        teachers = _read_block(summary, "Continuidad docente", 3)

        teacher_chart = []
        for row in workbook["Docentes DG"].iter_rows(min_row=2, values_only=True):
            if row[0] not in (None, "") and isinstance(row[1], (int, float)):
                teacher_chart.append((str(row[0]), float(row[1])))

        students_sheet = workbook["Tabla Dinamica Estudiantes"]
        headers = [str(cell.value or "").strip().upper() for cell in students_sheet[3]]
        total_days_column = headers.index("TOTAL") + 1
        student_start_column = total_days_column + 1
        total_students_column = headers.index("TOTAL", total_days_column) + 1
        total_row = next(
            row for row in range(4, students_sheet.max_row + 1)
            if str(students_sheet.cell(row, 1).value or "").strip().upper() == "TOTAL GENERAL"
        )
        student_days = [
            (headers[column - 1], float(students_sheet.cell(total_row, column).value or 0))
            for column in range(2, total_days_column)
        ]
        student_users = [
            (headers[column - 1], float(students_sheet.cell(total_row, column).value or 0))
            for column in range(student_start_column, total_students_column)
        ]

        design_sheet = workbook["Dise\u00f1o de Cursos"]
        design = {
            str(design_sheet.cell(5, column).value or ""): int(design_sheet.cell(6, column).value or 0)
            for column in range(3, 7)
        }
        return {
            "sheet_names": list(workbook.sheetnames),
            "indicators": indicators,
            "monthly": monthly,
            "courses": courses,
            "teachers": teachers,
            "teacher_chart": teacher_chart,
            "student_days": student_days,
            "student_users": student_users,
            "design": design,
        }
    finally:
        workbook.close()


def _line_chart(path, categories, series, title, ylabel):
    figure, axis = plt.subplots(figsize=(9.5, 5), dpi=190)
    figure.patch.set_facecolor('white')
    axis.set_facecolor('#FAFBFD')
    
    for name, values, color in series:
        axis.plot(categories, values, "o-", linewidth=3, markersize=8, label=name, color=color)
    
    axis.set_title(title, color=NAVY, fontweight="bold", fontsize=14, pad=16)
    axis.set_ylabel(ylabel, fontsize=11, color=NAVY, fontweight="600")
    axis.set_xlabel("", fontsize=11)
    axis.tick_params(axis='y', labelsize=10, colors=NAVY)
    axis.tick_params(axis='x', labelsize=10, colors=NAVY)
    axis.grid(axis="y", alpha=0.15, linestyle="--", linewidth=0.7)
    
    if len(series) > 1:
        axis.legend(frameon=True, fancybox=True, shadow=False, fontsize=10, 
                   loc='upper left', framealpha=0.95, edgecolor='#E3E6ED')
    
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color('#E3E6ED')
    axis.spines["bottom"].set_color('#E3E6ED')
    
    figure.tight_layout()
    figure.savefig(path, dpi=190, bbox_inches="tight", facecolor='white')
    plt.close(figure)


def _bar_chart(path, courses, title):
    names = [str(row[0]).replace("_", " ").title() for row in courses]
    values = [float(row[1] or 0) for row in courses]
    figure, axis = plt.subplots(figsize=(9.5, 5.5), dpi=190)
    figure.patch.set_facecolor('white')
    axis.set_facecolor('#FAFBFD')
    
    bars = axis.barh(names[::-1], values[::-1], color="#36BCE8", edgecolor="#0A7FA8", linewidth=1.2)
    axis.set_title(title, color=NAVY, fontweight="bold", fontsize=14, pad=16)
    
    # Agregar valores al lado de las barras
    for bar, value in zip(bars, values[::-1]):
        width = bar.get_width()
        axis.text(width + max(values or [1]) * 0.015, bar.get_y() + bar.get_height() / 2,
                  _number(value), va="center", fontsize=10, fontweight="600", color=NAVY)
    
    axis.set_xlabel("Eventos estudiantiles", fontsize=11, fontweight="600", color=NAVY)
    axis.tick_params(axis='x', labelsize=10, colors=NAVY)
    axis.tick_params(axis='y', labelsize=10, colors=NAVY)
    axis.grid(axis="x", alpha=0.15, linestyle="--", linewidth=0.7)
    
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color('#E3E6ED')
    axis.spines["bottom"].set_color('#E3E6ED')
    
    figure.tight_layout()
    figure.savefig(path, dpi=190, bbox_inches="tight", facecolor='white')
    plt.close(figure)


def _pie_chart(path, design, title):
    values = [design.get("Sin contenido", 0), design.get("Con contenido", 0)]
    labels = ["Sin contenido", "Con contenido"]
    colors = [GOLD, BLUE]
    figure, axis = plt.subplots(figsize=(8, 5.4), dpi=240)
    figure.patch.set_facecolor('white')

    if sum(values):
        visible = [(label, value, color) for label, value, color in zip(labels, values, colors) if value]
        chart_labels, chart_values, chart_colors = zip(*visible)
        wedges, _texts, autotexts = axis.pie(
            chart_values,
            autopct="%1.1f%%",
            colors=chart_colors,
            startangle=90,
            counterclock=False,
            textprops={"weight": "bold", "fontsize": 11},
            wedgeprops={"edgecolor": "white", "linewidth": 3},
            pctdistance=0.68,
        )
        for autotext in autotexts:
            autotext.set_color("white")
            autotext.set_fontsize(12)
            autotext.set_fontweight("bold")
        axis.legend(
            wedges, chart_labels, loc="lower center", bbox_to_anchor=(0.5, -0.08),
            ncol=len(chart_labels), frameon=False, fontsize=11,
        )
    else:
        axis.text(0.5, 0.5, "Sin datos de diseño", ha="center", va="center", 
                 color=NAVY, fontsize=13, fontweight="bold")

    axis.set_aspect("equal", adjustable="box")
    axis.set_title(title, color=NAVY, fontweight="bold", fontsize=14, pad=16)
    figure.tight_layout()
    figure.savefig(path, dpi=300, bbox_inches="tight", facecolor='white')
    plt.close(figure)


def _create_charts(directory, data, program, period):
    paths = [Path(directory) / f"chart_{index}.png" for index in range(6)]
    monthly = data["monthly"]
    categories = [MONTH_NAMES.get(str(row[0]).upper(), str(row[0])) for row in monthly]
    _line_chart(paths[0], categories, [
        ("Estudiantes", [row[1] or 0 for row in monthly], BLUE),
        ("Docentes", [row[3] or 0 for row in monthly], GOLD),
    ], "Eventos mensuales por tipo de usuario", "Eventos registrados")
    teacher = data["teacher_chart"]
    _line_chart(paths[1], [MONTH_NAMES.get(row[0].upper(), row[0]) for row in teacher],
                [("PROMEDIO", [row[1] for row in teacher], BLUE)],
                "D\u00edas al mes de uso del Campus Virtual por parte de los docentes\n"
                f"de la facultad de {program} {period}", "Promedio de d\u00edas de uso")
    days = data["student_days"]
    _line_chart(paths[2], [MONTH_NAMES.get(row[0].upper(), row[0]) for row in days],
                [("Promedio de días de uso", [row[1] for row in days], BLUE)],
                "D\u00edas del mes de uso del Campus Virtual por parte de los estudiantes\n"
                f"de la facultad de {program} {period}", "Promedio de d\u00edas de uso")
    users = data["student_users"]
    _line_chart(paths[3], [MONTH_NAMES.get(row[0].upper(), row[0]) for row in users],
                [("Promedio de estudiantes", [row[1] for row in users], GOLD)],
                "Promedio de estudiantes que usaron el Campus Virtual de la facultad\n"
                f"de {program} {period}", "Promedio de estudiantes")
    _bar_chart(paths[4], data["courses"], "Cursos con mayor actividad estudiantil")
    _pie_chart(paths[5], data["design"], "Diseño de Cursos")
    return paths


def _fill_table(table, headers, rows):
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    
    values = [headers, *rows]
    for row_index, table_row in enumerate(table.rows):
        row_values = values[row_index] if row_index < len(values) else [""] * len(table.columns)
        for column_index, cell in enumerate(table_row.cells):
            cell.text = str(row_values[column_index] if column_index < len(row_values) else "")
            
            # Dar estilo a la fila de encabezados
            if row_index == 0:
                paragraph = cell.paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.bold = True
                    run.font.size = Pt(11)
                    run.font.color.rgb = RGBColor(255, 255, 255)  # Blanco
                # Color de fondo azul para encabezado
                from docx.oxml import parse_xml
                shading_elm = parse_xml(r'<w:shd {} w:fill="2878B5"/>'.format('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'))
                cell._element.get_or_add_tcPr().append(shading_elm)
            else:
                # Dar estilo a las filas de datos
                paragraph = cell.paragraphs[0]
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in paragraph.runs:
                    run.font.size = Pt(10)
                    run.font.color.rgb = RGBColor(33, 21, 104)  # Texto oscuro


def _replace_images(document, image_paths):
    if len(document.inline_shapes) < len(image_paths):
        raise ValueError("La plantilla no contiene los seis espacios de graficas esperados.")
    original_shapes = list(document.inline_shapes)[:len(image_paths)]
    for shape, image_path in zip(original_shapes, image_paths):
        old_drawing = shape._inline.getparent()
        run = old_drawing.getparent()
        with Image.open(image_path) as source_image:
            image_ratio = source_image.width / source_image.height
        max_width, max_height = int(shape.width), int(shape.height)
        width = min(max_width, int(max_height * image_ratio))
        height = int(width / image_ratio)
        temporary_paragraph = document.add_paragraph()
        temporary_run = temporary_paragraph.add_run()
        new_shape = temporary_run.add_picture(
            str(image_path), width=width, height=height
        )
        new_drawing = new_shape._inline.getparent()
        run.replace(old_drawing, new_drawing)
        temporary_paragraph._element.getparent().remove(temporary_paragraph._element)


def _replace_paragraph(document, prefix, text):
    for paragraph in document.paragraphs:
        if paragraph.text.strip().startswith(prefix):
            paragraph.text = text
            return True
    return False


def _replace_paragraph_group(document, prefix, texts):
    """Actualiza un bloque narrativo sin cambiar su lugar en la plantilla."""
    for index, paragraph in enumerate(document.paragraphs):
        if paragraph.text.strip().startswith(prefix):
            for offset, text in enumerate(texts):
                if index + offset < len(document.paragraphs):
                    document.paragraphs[index + offset].text = text
            return True
    return False


def _replace_containing(document, fragment, text):
    for paragraph in document.paragraphs:
        if fragment.casefold() in paragraph.text.casefold():
            paragraph.text = text
            return True
    return False


def _replace_marker(document, marker, text):
    """Reemplaza un marcador tanto en párrafos normales como en cuadros de texto."""
    replaced = False
    for paragraph in document.paragraphs:
        if marker in paragraph.text:
            paragraph.text = paragraph.text.replace(marker, text)
            replaced = True
    for node in document.element.iter(qn("w:t")):
        if marker in (node.text or ""):
            node.text = node.text.replace(marker, text)
            replaced = True
    return replaced


def _replace_cover_fields(document, program, period):
    """Actualiza textos de portada que Word guarda dentro de cuadros de texto."""
    for node in document.element.iter(qn("w:t")):
        original = node.text or ""
        updated = original.replace("{{PROGRAMA}}", program).replace("{{PERIODO}}", period)
        updated = re.sub(
            r"Ingenier.a de Sistemas", program, original,
            flags=re.IGNORECASE,
        ) if updated == original else updated
        updated = updated.replace("2026-1", period)
        if updated != original:
            node.text = updated


def generate_word_report(workbook_path, output_path, program, period, template_path=None):
    """Genera el DOCX final conservando estructura, estilos y posiciones de la plantilla."""
    workbook_path = Path(workbook_path)
    output_path = Path(output_path)
    template_path = Path(template_path) if template_path else _bundled_template_path()
    if not workbook_path.is_file():
        raise FileNotFoundError("El Excel terminado no existe.")
    if not template_path.is_file():
        raise FileNotFoundError(
            "No se encontro la plantilla institucional de Word. "
            f"Debe existir en: {template_path}"
        )

    data = _extract_data(workbook_path)
    indicators = {str(row[0]): row[1:] for row in data["indicators"]}
    total_events = float(indicators.get("Eventos totales", (0, ""))[0] or 0)
    design_total = data["design"].get("Total", 0)
    with_content = data["design"].get("Con contenido", 0)
    content_percent = (with_content * 100 / design_total) if design_total else 0

    with TemporaryDirectory(prefix="informe_word_") as temporary:
        images = _create_charts(temporary, data, program, period)
        document = Document(template_path)
        _replace_images(document, images)
        _replace_cover_fields(document, program, period)

        indicator_rows = []
        for label, result, reading in data["indicators"]:
            decimals = 1 if isinstance(result, float) and not result.is_integer() else 0
            suffix = " promedio" if str(label).startswith("D\u00edas activos") else (
                " eventos" if str(label).startswith("Actividad") else ""
            )
            indicator_rows.append((label, _number(result, decimals) + suffix, reading))
        monthly_rows = [
            (MONTH_NAMES.get(str(row[0]).upper(), row[0]), _number(row[1]), _number(row[2]), _number(row[3]))
            for row in data["monthly"]
        ]
        teacher_rows = [(row[0], row[1], _number(row[2])) for row in data["teachers"]]
        course_rows = [(row[0], _number(row[1]), _number(row[2]), _number(row[3])) for row in data["courses"]]
        _fill_table(document.tables[0], ("Indicador", "Resultado", "Lectura"), indicator_rows)
        _fill_table(document.tables[2], ("Mes", "Eventos estudiantes", "Estudiantes activos", "Eventos docentes"), monthly_rows)
        _fill_table(document.tables[3], ("Curso", "Docente", "D\u00edas activos"), teacher_rows)
        _fill_table(document.tables[4], ("Curso", "Eventos", "Estudiantes \u00fanicos", "D\u00edas activos"), course_rows)

        _replace_paragraph(document, "Durante el semestre", (
            f"Durante el periodo {period} se analizaron {_number(total_events)} eventos de Open LMS "
            f"correspondientes al programa de {program}. Los resultados permiten reconocer el nivel de "
            "participacion de estudiantes y docentes, la continuidad mensual y los cursos con mayor actividad."
        ))
        _replace_paragraph(document, "Este informe", (
            f"Este informe estad\u00edstico presenta el uso de la plataforma Open LMS para el programa de "
            f"{program} durante el periodo {period}. Fue elaborado por el equipo del Campus Virtual."
        ))
        _replace_paragraph(document, "Para la", (
            f"Para la elaboraci\u00f3n del informe se analizaron {_number(total_events)} registros del sistema "
            "de seguimiento del Campus Virtual. La informaci\u00f3n fue consolidada autom\u00e1ticamente en Excel."
        ))
        sheet_descriptions = {
            "Original": "Datos originales y campos de fecha preparados.",
            "Tabla Dinamica Docentes": "Actividad docente consolidada por curso y mes.",
            "Docentes DG": "Representación gráfica de la actividad docente mensual.",
            "Tabla Dinamica Estudiantes": "Días activos y estudiantes únicos por curso y mes.",
            "Estudiantes DG": "Representación gráfica de los días de actividad estudiantil.",
            "Estudiantes DG2": "Promedio mensual de estudiantes que usaron el Campus Virtual.",
            "Tabla Dinamica Actividades": "Cantidad de acciones registradas en cada curso.",
            "Resumen Informe": "Indicadores y datos consolidados para el informe institucional.",
            "Diseño de Cursos": "Cantidad de cursos con contenido y sin contenido.",
        }
        sheet_lines = [
            f"{index}. Hoja «{name}»: {sheet_descriptions.get(name, 'Información complementaria del reporte.')}"
            for index, name in enumerate(data["sheet_names"], 1)
        ]
        sheet_lines.extend([""] * (10 - len(sheet_lines)))
        sheet_intro = (
            f"El archivo Excel adjunto contiene {len(data['sheet_names'])} hojas con el detalle y "
            f"los resultados del programa de {program} para el periodo {period}."
        )
        if _replace_marker(document, "{{DESCRIPCION_HOJAS}}", sheet_intro):
            for index, line in enumerate(sheet_lines[:10], 1):
                _replace_marker(document, f"{{{{HOJA_{index}}}}}", line)
        else:
            _replace_paragraph_group(document, "Este informe podr", [
                sheet_intro, *sheet_lines[:10],
            ])
        if data["monthly"]:
            peak = max(data["monthly"], key=lambda row: (row[1] or 0) + (row[3] or 0))
            monthly_text = (
                f"La mayor actividad se registr\u00f3 en {MONTH_NAMES.get(str(peak[0]).upper(), peak[0])}, "
                f"con {_number((peak[1] or 0) + (peak[3] or 0))} eventos combinados. La tabla compara "
                "el volumen de eventos con la cantidad de estudiantes activos por mes."
            )
            if not _replace_marker(document, "{{ANALISIS_MENSUAL}}", monthly_text):
                _replace_paragraph(document, "La actividad se concentr\u00f3", monthly_text)
        if teacher_rows:
            teacher_details = [
                f"{row[1]} en {row[0]}, con {row[2]} días activos durante el periodo."
                for row in teacher_rows[:3]
            ]
            teacher_details.extend([""] * (3 - len(teacher_details)))
            teacher_intro = (
                f"Los docentes con mayor continuidad se identificaron mediante los d\u00edas diferentes con "
                f"actividad. El primer lugar corresponde a {teacher_rows[0][1]} en {teacher_rows[0][0]}, "
                f"con {teacher_rows[0][2]} d\u00edas activos."
            )
            if _replace_marker(document, "{{ANALISIS_DOCENTES}}", teacher_intro):
                for index, detail in enumerate(teacher_details, 1):
                    _replace_marker(document, f"{{{{DOCENTE_{index}}}}}", detail)
            else:
                _replace_paragraph_group(document, "Con un uso que va", [teacher_intro, *teacher_details])
        if course_rows:
            course_details = [
                f"{row[0]}: {row[1]} eventos, {row[2]} estudiantes únicos y {row[3]} días activos."
                for row in course_rows[:3]
            ]
            course_details.extend([""] * (3 - len(course_details)))
            course_intro = (
                f"El curso con mayor volumen de actividad estudiantil fue {course_rows[0][0]}, con "
                f"{course_rows[0][1]} eventos, {course_rows[0][2]} estudiantes \u00fanicos y "
                f"{course_rows[0][3]} d\u00edas activos."
            )
            if _replace_marker(document, "{{ANALISIS_ESTUDIANTES}}", course_intro):
                for index, detail in enumerate(course_details, 1):
                    _replace_marker(document, f"{{{{CURSO_{index}}}}}", detail)
            else:
                _replace_paragraph_group(document, "Con un acceso en promedio", [
                    course_intro, "Los cursos destacados son:", *course_details,
                ])
        design_text = (
            f"El programa de {program} cuenta con {design_total} cursos evaluados: {with_content} con "
            f"contenido y {data['design'].get('Sin contenido', 0)} sin contenido. Esto equivale a "
            f"{_number(content_percent, 1)} % de cursos con contenido."
        )
        if not _replace_marker(document, "{{ANALISIS_DISENO}}", design_text):
            _replace_containing(document, "cuenta con un total de 59 cursos", design_text)
        captions = (
            ("Ilustración 1", "Ilustración 1. Eventos mensuales por tipo de usuario."),
            ("Ilustración 2", "Ilustración 2. Días al mes de uso del Campus Virtual por parte de los docentes "
             f"de la facultad de {program} {period}."),
            ("Ilustración 3", "Ilustración 3. Días del mes de uso del Campus Virtual por parte de los estudiantes "
             f"de la facultad de {program} {period}."),
            ("Ilustración 4", "Ilustración 4. Promedio de estudiantes que usaron el Campus Virtual de la facultad "
             f"de {program} {period}."),
            ("Ilustración 5", "Ilustración 5. Cursos con mayor actividad estudiantil."),
            ("Ilustración 6", "Ilustración 6. Diseño de Cursos."),
        )
        for prefix, caption in captions:
            _replace_paragraph(document, prefix, caption)
        for paragraph in document.paragraphs:
            if "2026-1" in paragraph.text and period != "2026-1":
                paragraph.text = paragraph.text.replace("2026-1", period)
            updated_text = re.sub(
                r"Ingenier.a de Sistemas", program, paragraph.text,
                flags=re.IGNORECASE,
            )
            if updated_text != paragraph.text:
                paragraph.text = updated_text

        output_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_output = output_path.with_name(output_path.stem + "_EN_PROCESO.docx")
        document.save(temporary_output)
        temporary_output.replace(output_path)
    return output_path
