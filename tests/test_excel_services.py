import pandas as pd
import pytest
from openpyxl import load_workbook

from app.services.csv_service import iter_csv_chunks, prepare_original_data, read_csv_file
from app.services.excel_service import ExcelProcess, suggested_filename


def test_read_and_prepare_original_csv(tmp_path):
    csv_path = tmp_path / "moodle.csv"
    csv_path.write_text("Curso;FechaUnix;Usuario\nÁlgebra;1704067200;ana\n", encoding="utf-8")

    frame = read_csv_file(csv_path)
    prepared = prepare_original_data(frame)

    assert list(frame.columns) == ["Curso", "FechaUnix", "Usuario"]
    assert list(prepared.columns) == ["Curso", "FechaUnix", "Fecha", "Mes", "Dia", "Usuario"]
    assert str(prepared.loc[0, "Fecha"]) == "2023-12-31"
    assert prepared.loc[0, "Mes"] == 12
    assert prepared.loc[0, "Dia"] == 31


def test_excel_process_uses_one_workbook_and_limits_preview(tmp_path):
    frame = pd.DataFrame({"Curso": [f"Curso {index}" for index in range(250)]})
    process = ExcelProcess()
    process.create_original(frame)

    headers, rows, total = process.preview_sheet("Original", limit=200)
    destination = tmp_path / "resultado.xlsx"
    process.save_as(destination)

    assert process.sheet_names() == ["Original"]
    assert headers == ["Curso"]
    assert len(rows) == 200
    assert total == 250
    assert destination.is_file()


def test_large_csv_is_written_in_chunks(tmp_path):
    csv_path = tmp_path / "grande.csv"
    csv_path.write_text("Curso;FechaUnix\n" + "\n".join(f"Curso {i};1704067200" for i in range(1200)), encoding="utf-8")
    process = ExcelProcess()

    rows, columns = process.create_original_from_chunks(
        iter_csv_chunks(csv_path, chunksize=100, prepare=True)
    )

    assert (rows, columns) == (1200, 5)
    assert process.preview_sheet("Original", limit=25)[2] == 1200


def test_suggested_filename_normalizes_program():
    assert suggested_filename("2026-1", "Ingeniería de Sistemas") == "Informe_2026-1_Ingeniería_de_Sistemas.xlsx"


def test_fechaunix_in_milliseconds_is_detected(tmp_path):
    csv_path = tmp_path / "milisegundos.csv"
    csv_path.write_text("FechaUnix\n1704067200000\n", encoding="utf-8")

    prepared = prepare_original_data(read_csv_file(csv_path))

    assert str(prepared.loc[0, "Fecha"]) == "2023-12-31"
    assert prepared.loc[0, "Mes"] == 12
    assert prepared.loc[0, "Dia"] == 31


def test_crea_tabla_docentes_con_dias_distintos_y_meses_dinamicos():
    original = pd.DataFrame(
        {
            "curso": [
                "Curso A", "Curso A", "Curso A", "Curso A", "Curso A",
                "Curso A", "Curso A", "Curso B",
            ],
            "usuario": [
                "Ana", "Ana", "Ana", "Ana", "Ana", "Ana", "Estudiante", "Luis",
            ],
            "rol": [
                "editingteacher", "editingteacher", "editingteacher",
                "editingteacher", "editingteacher", " EditingTeacher ",
                "student", "editingteacher",
            ],
            "Mes": [2, 2, 2, 3, 3, 3, 2, 3],
            "Dia": [1, 1, 2, 1, 3, 3, 9, 8],
            "Fecha": pd.to_datetime(
                [
                    "2026-02-01", "2026-02-01", "2026-02-02",
                    "2026-03-01", "2026-03-03", "2026-03-03",
                    "2026-02-09", "2026-03-08",
                ]
            ),
        }
    )
    proceso = ExcelProcess()
    proceso.create_original_from_chunks([original])

    cantidad_filas, meses = proceso.crear_tabla_docentes()

    assert cantidad_filas == 2
    assert meses == ["FEB", "MAR"]
    assert proceso.sheet_names() == ["Original", "Tabla Dinamica Docentes"]
    encabezados, filas, total = proceso.preview_sheet("Tabla Dinamica Docentes")
    assert encabezados == ["CURSO", "DOCENTE", "FEB", "MAR", "TOTAL"]
    assert total == 3
    assert filas[0] == ("Curso A", "Ana", 2, 2, 4)
    assert filas[1] == ("Curso B", "Luis", 0, 1, 1)
    assert filas[2] == ("PROMEDIO", None, 1, 1.5, None)

    libro = load_workbook(proceso.path)
    hoja = libro["Tabla Dinamica Docentes"]
    assert hoja.freeze_panes == "C2"
    assert hoja["A1"].font.bold is True
    assert hoja["C2"].alignment.horizontal == "center"
    assert hoja["E2"].font.bold is True
    assert hoja["A4"].value == "PROMEDIO"
    assert hoja["A4"].font.bold is True
    libro.close()


def test_tabla_docentes_reemplaza_la_misma_hoja_al_repetirse():
    original = pd.DataFrame(
        {
            "curso": ["Curso A"],
            "usuario": ["Ana"],
            "rol": ["editingteacher"],
            "Mes": [4],
            "Dia": [7],
        }
    )
    proceso = ExcelProcess()
    proceso.create_original(original)

    proceso.crear_tabla_docentes()
    proceso.crear_tabla_docentes()

    assert proceso.sheet_names() == ["Original", "Tabla Dinamica Docentes"]


def test_tabla_docentes_exige_registros_de_docentes():
    proceso = ExcelProcess()
    proceso.create_original(
        pd.DataFrame(
            {
                "curso": ["Curso A"],
                "usuario": ["Estudiante"],
                "rol": ["student"],
                "Mes": [2],
                "Dia": [1],
            }
        )
    )

    with pytest.raises(ValueError, match="editingteacher"):
        proceso.crear_tabla_docentes()
