import pandas as pd

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
