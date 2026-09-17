import unicodedata
import sys
import threading
from types import SimpleNamespace
from pathlib import Path

import pytest

import docx2pdf
from app.services import pdf_report_service
from app.services.pdf_report_service import (
    _convert_with_docx2pdf,
    _normalize_fs_path,
)


def test_normalize_fs_path_finds_file_with_other_unicode_form(tmp_path):
    target = tmp_path / unicodedata.normalize("NFC", "ESPECIALIZACIÓN.docx")
    target.write_bytes(b"fake")
    requested = tmp_path / unicodedata.normalize("NFD", "ESPECIALIZACIÓN.docx")
    assert _normalize_fs_path(requested) == target


def test_normalize_fs_path_prefers_nfc_for_missing_file(tmp_path):
    missing = tmp_path / "informe.docx"
    assert _normalize_fs_path(missing) == missing


def test_docx2pdf_raises_when_word_cannot_see_file(tmp_path, monkeypatch):
    monkeypatch.setattr(docx2pdf, "convert", lambda *args: None)
    with pytest.raises(FileNotFoundError):
        _convert_with_docx2pdf(tmp_path / "no_existe.docx", tmp_path / "salida.pdf")


def test_docx2pdf_retries_once_on_mac(tmp_path, monkeypatch):
    source = tmp_path / "informe.docx"
    source.write_bytes(b"fake")
    calls = []

    def fake_convert(word, pdf):
        calls.append((word, pdf))
        if len(calls) == 1:
            raise RuntimeError("Error: Mensaje incomprensible.")
        Path(pdf).write_bytes(b"pdf")

    monkeypatch.setattr(docx2pdf, "convert", fake_convert)
    monkeypatch.setattr(pdf_report_service.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(pdf_report_service.time, "sleep", lambda seconds: None)
    _convert_with_docx2pdf(source, tmp_path / "salida.pdf")
    assert len(calls) == 2


def test_docx2pdf_fails_fast_off_mac(tmp_path, monkeypatch):
    source = tmp_path / "informe.docx"
    source.write_bytes(b"fake")
    calls = []

    def fake_convert(word, pdf):
        calls.append((word, pdf))
        raise RuntimeError("Error: Mensaje incomprensible.")

    monkeypatch.setattr(docx2pdf, "convert", fake_convert)
    monkeypatch.setattr(pdf_report_service.platform, "system", lambda: "Windows")
    with pytest.raises(RuntimeError):
        _convert_with_docx2pdf(source, tmp_path / "salida.pdf")
    assert len(calls) == 1


@pytest.mark.parametrize("fail_export", [False, True])
def test_word_com_stays_in_one_thread_and_cleans_up(tmp_path, monkeypatch, fail_export):
    events = []
    source = tmp_path / "informe.docx"
    destination = tmp_path / "informe.pdf"

    def record(name):
        events.append((name, threading.get_ident()))

    class Document:
        def ExportAsFixedFormat(self, path, file_format):
            record("export")
            assert path == str(destination)
            assert file_format == 17
            if fail_export:
                raise RuntimeError("export failed")
            Path(path).write_bytes(b"%PDF-1.7")

        def Close(self, save_changes):
            assert save_changes is False
            record("close")

    class Word:
        def __init__(self):
            self.Documents = self

        def Open(self, path, ReadOnly):
            record("open")
            assert path == str(source)
            assert ReadOnly is True
            return Document()

        def Quit(self):
            record("quit")

    def dispatch(name):
        assert name == "Word.Application"
        record("dispatch")
        return Word()

    monkeypatch.setattr(pdf_report_service.platform, "system", lambda: "Windows")
    monkeypatch.setitem(sys.modules, "pythoncom", SimpleNamespace(
        CoInitialize=lambda: record("initialize"),
        CoUninitialize=lambda: record("uninitialize"),
    ))
    monkeypatch.setitem(sys.modules, "win32com", SimpleNamespace(
        client=SimpleNamespace(DispatchEx=dispatch),
    ))
    if fail_export:
        with pytest.raises(RuntimeError, match="export failed"):
            pdf_report_service._convert_with_win32com(source, destination)
    else:
        pdf_report_service._convert_with_win32com(source, destination)
        assert destination.read_bytes().startswith(b"%PDF")
    assert [name for name, _ in events] == [
        "initialize", "dispatch", "open", "export", "close", "quit", "uninitialize"
    ]
    assert len({thread for _, thread in events}) == 1
    assert events[0][1] != threading.get_ident()


def test_windows_pdf_fallback_works_without_console(tmp_path, monkeypatch):
    source = tmp_path / "informe.docx"
    source.write_bytes(b"docx")

    def missing_libreoffice(*args):
        raise FileNotFoundError("LibreOffice")

    def unexpected_docx2pdf(*args):
        pytest.fail("Windows must not use the console-dependent converter")

    def export_word(word, pdf):
        pdf.write_bytes(b"%PDF-1.7")

    monkeypatch.setattr(pdf_report_service.platform, "system", lambda: "Windows")
    monkeypatch.setattr(pdf_report_service, "_convert_with_libreoffice", missing_libreoffice)
    monkeypatch.setattr(pdf_report_service, "_convert_with_docx2pdf", unexpected_docx2pdf)
    monkeypatch.setattr(pdf_report_service, "_convert_with_win32com", export_word)
    monkeypatch.setattr(sys, "stderr", None)
    monkeypatch.setattr(sys, "stdout", None)
    assert pdf_report_service.convert_word_to_pdf(source).read_bytes().startswith(b"%PDF")
