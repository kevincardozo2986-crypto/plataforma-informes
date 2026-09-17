import pytest

from app.services.report_path_service import (
    POSTGRADUATE_TYPES,
    build_excel_path,
    build_report_directory,
    build_word_path,
    copy_source_csv,
    prepare_report_paths,
    sanitize_name,
)


@pytest.mark.parametrize("modality", ["Presencial", "Virtual", "Presencial-Virtual"])
@pytest.mark.parametrize("postgraduate_type", POSTGRADUATE_TYPES)
def test_postgraduate_directory_includes_type(tmp_path, modality, postgraduate_type):
    paths = prepare_report_paths(
        tmp_path, "2026-1", "Posgrado", modality, "Programa", "datos.csv",
        postgraduate_type=postgraduate_type,
    )
    assert paths.directory == (
        tmp_path / "INFORMES USO PLATAFORMA 2026-1"
        / f"Posgrado_{modality}" / postgraduate_type / "PROGRAMA"
    )
    assert paths.source_csv.parent == paths.excel.parent == paths.directory


def test_postgraduate_requires_valid_selection_when_provided(tmp_path):
    with pytest.raises(ValueError, match="tipo de posgrado"):
        build_report_directory(tmp_path, "2026-1", "Posgrado", "Virtual", "Programa", "")


def test_pregraduate_ignores_previous_postgraduate_selection(tmp_path):
    assert build_report_directory(
        tmp_path, "2026-1", "Pregrado", "Virtual", "Programa", "Doctorado"
    ) == build_report_directory(tmp_path, "2026-1", "Pregrado", "Virtual", "Programa")


def test_builds_institutional_directory_without_duplicates(tmp_path):
    expected = (
        tmp_path
        / "INFORMES USO PLATAFORMA 2026-1"
        / "Pregrado_Presencial"
        / "INGENIERÍA DE SISTEMAS"
    )

    result = build_report_directory(
        tmp_path, "2026-1", "Pregrado", "Presencial", "Ingeniería de Sistemas"
    )

    assert result == expected


def test_prepares_paths_and_preserves_csv_filename(tmp_path):
    source = tmp_path / "Informe_Moodle.csv"
    source.write_text("curso\nA", encoding="utf-8")

    paths = prepare_report_paths(
        tmp_path, "2026-1", "Pregrado", "Virtual", "Ingeniería de Sistemas", source
    )

    assert paths.source_csv.name == "Informe_Moodle.csv"
    assert paths.excel.name == "Informe_2026-1.xlsx"
    assert paths.word is None
    assert paths.pdf is None


def test_copy_requires_explicit_overwrite(tmp_path):
    source = tmp_path / "origen.csv"
    destination = tmp_path / "destino" / "origen.csv"
    source.write_text("primero", encoding="utf-8")
    copy_source_csv(source, destination)
    source.write_text("segundo", encoding="utf-8")

    try:
        copy_source_csv(source, destination)
        assert False, "Debió impedir la sobrescritura silenciosa"
    except FileExistsError:
        pass

    copy_source_csv(source, destination, overwrite=True)
    assert destination.read_text(encoding="utf-8") == "segundo"


def test_sanitizes_windows_names_and_builds_explicit_program_code(tmp_path):
    assert sanitize_name(' Ingeniería: Sistemas* ', uppercase=True) == "INGENIERÍA- SISTEMAS-"
    assert build_excel_path(tmp_path, "2026-1").name == "Informe_2026-1.xlsx"
    assert build_word_path(tmp_path, "2026-1", "ING SIS").name == "Informe_2026-1_ING_SIS.docx"
