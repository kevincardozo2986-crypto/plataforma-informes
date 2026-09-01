import pandas as pd
from docx import Document
from openpyxl import load_workbook

from app.services.excel_service import ExcelProcess
from app.services.word_report_service import generate_word_report


def test_generates_word_from_finished_excel_and_preserves_template(tmp_path):
    original = pd.DataFrame(
        {
            "curso": ["Curso A", "Curso A", "Curso A", "Curso B", "Curso B", "Curso A"],
            "idusuario": [1, 1, 10, 11, 11, 10],
            "usuario": ["Docente Uno", "Docente Uno", "Ana", "Beto", "Beto", "Ana"],
            "rol": ["editingteacher", "editingteacher", "student", "student", "student", "student"],
            "Mes": [2, 3, 2, 2, 3, 3],
            "Dia": [1, 2, 3, 4, 5, 6],
            "accion": ["updated", "viewed", "viewed", "created", "viewed", "submitted"],
        }
    )
    process = ExcelProcess(tmp_path / "Informe.xlsx")
    process.create_original_from_chunks([original])
    process.crear_tabla_docentes()
    process.crear_grafica_docentes("Ingenieria de Sistemas", "2026-1")
    process.crear_tabla_estudiantes("Ingenieria de Sistemas", "2026-1")
    process.crear_grafica_estudiantes("Ingenieria de Sistemas", "2026-1")
    process.crear_tabla_actividades("Ingenieria de Sistemas", "2026-1")
    process.crear_diseno_cursos("Ingenieria de Sistemas", "2026-1")

    workbook = load_workbook(process.path, read_only=False, data_only=True)
    assert "Resumen Informe" in workbook.sheetnames
    assert len(workbook["Resumen Informe"]._charts) == 2
    workbook.close()

    destination = tmp_path / "Informe_2026-1_ING_SIS.docx"
    result = generate_word_report(
        process.path, destination, "Ingenieria de Sistemas", "2026-1"
    )

    assert result == destination
    assert destination.is_file()
    document = Document(destination)
    assert len(document.tables) == 5
    assert len(document.inline_shapes) == 6
    assert document.tables[0].cell(1, 1).text == "6"
    assert document.tables[2].cell(1, 0).text == "Febrero"
    assert any("Ingenieria de Sistemas" in paragraph.text for paragraph in document.paragraphs)
