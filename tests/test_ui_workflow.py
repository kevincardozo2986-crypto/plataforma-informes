import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from openpyxl import Workbook
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import QApplication, QPushButton, QWidget

from app.database import database
from app.services.auth_service import create_user
from app.services.report_option_service import delete_report_option, list_report_options
from app.services.report_path_service import prepare_report_paths
from app.ui import excel_process_window as excel_ui
from app.ui import window_chrome
from app.ui.word_report_window import WordReportWindow


@pytest.fixture(scope="module")
def application():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def page(application, tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "app.db")
    database.initialize_database()
    user = create_user("test", "password", "Test")
    monkeypatch.setattr(excel_ui, "anchor_bottom_right", lambda *args: None)
    widget = excel_ui.ExcelProcessWindow(user)
    widget.base_directory = tmp_path
    yield widget
    widget.close()
    widget.deleteLater()
    application.processEvents()


def test_doctorate_then_specialization_unlocks_controls(page, tmp_path):
    page.level.setCurrentText("Posgrado")
    page.postgraduate_type.setCurrentText("Doctorado")
    page.csv_path = tmp_path / "source.csv"
    page._update_destination()
    page._csv_loaded((7, page.report_paths))
    assert not page.postgraduate_type.isEnabled()
    page._volver_al_dashboard()
    assert page.postgraduate_type.isEnabled()
    assert page.select_csv_button.isEnabled()
    page.postgraduate_type.setCurrentText("Especialización")
    page.csv_path = tmp_path / "other.csv"
    page._update_destination()
    assert "Especialización" in page.report_paths.directory.parts
    assert "Doctorado" not in page.report_paths.directory.parts
    assert page.load_button.isEnabled()
    assert all(b.isEnabled() for b in page.findChildren(QPushButton, "addOptionButton"))


def test_new_report_preserves_file_and_unlocks_saved_report(page, tmp_path):
    old = tmp_path / "saved.xlsx"
    old.write_bytes(b"keep")
    page._configuration_locked = True
    page._set_configuration_enabled(False)
    page._report_saved = True
    page._nuevo_informe()
    assert old.read_bytes() == b"keep"
    assert page.level.isEnabled()
    assert not page._configuration_locked


@pytest.mark.parametrize("fail", [False, True])
def test_background_callbacks_run_on_ui_thread_and_restore_buttons(page, application, fail):
    called = []
    page.steps[3].set_state("completed")
    def operation(progress):
        if fail:
            raise ValueError("test error")
        return 42
    def callback(result):
        called.append((QThread.currentThread() == application.thread(), result))
    page._start_background(operation, callback, callback)
    deadline = time.monotonic() + 10
    while page._thread is not None and time.monotonic() < deadline:
        application.processEvents()
        time.sleep(0.01)
    assert page._thread is None
    assert called == [(True, "test error" if fail else 42)]
    assert page.steps[3].view_button.isEnabled()
    assert page.new_report_button.isEnabled()


def test_custom_levels_and_modalities_build_paths(tmp_path):
    paths = prepare_report_paths(tmp_path, "2026-1", "Educación continua", "Híbrida", "Programa", "input.csv")
    assert "Educación continua_Híbrida" in paths.directory.parts


def test_deleted_options_stay_deleted_after_restart(page):
    user = page.usuario_actual
    delete_report_option(user, "modality", "Virtual")
    database.initialize_database()
    create_user("another", "password", "Another")
    assert "Virtual" not in list_report_options("modality")


def test_mac_uses_native_window_frame(application, monkeypatch):
    monkeypatch.setattr(window_chrome.sys, "platform", "darwin")
    widget = QWidget()
    bar = window_chrome.preparar_ventana_sin_marco(widget, "Prueba")
    assert not widget.windowFlags() & Qt.FramelessWindowHint
    assert widget.windowTitle() == "Prueba"
    assert bar.height() == 0
    widget.close()


def test_word_reads_program_from_workbook_not_filename(tmp_path):
    path = tmp_path / "Informe_2026-1.xlsx"
    book = Workbook()
    book.active.title = "Resumen Informe"
    book.active["A1"] = "Resumen del informe Open LMS - Especialización en Educación 2026-1"
    book.save(path)
    book.close()
    assert WordReportWindow._read_report_identity(path) == ("Especialización en Educación", "2026-1")
