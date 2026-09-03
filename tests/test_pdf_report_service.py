import unicodedata
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
