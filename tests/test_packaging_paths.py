import sys
from pathlib import Path

from app.database import database


def test_source_database_stays_in_project(monkeypatch):
    monkeypatch.delenv("SANTOTO_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "frozen", False, raising=False)
    assert database.database_path() == database.PROJECT_ROOT / "data/app.db"


def test_frozen_windows_database_is_outside_bundle(monkeypatch, tmp_path):
    monkeypatch.delenv("SANTOTO_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert database.database_path() == tmp_path / "SantotoTunjaInformes/app.db"


def test_frozen_macos_database_is_outside_bundle(monkeypatch):
    monkeypatch.delenv("SANTOTO_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "platform", "darwin")
    assert database.database_path() == Path.home() / "Library/Application Support/SantotoTunjaInformes/app.db"


def test_custom_database_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("SANTOTO_DATA_DIR", str(tmp_path))
    assert database.database_path() == tmp_path / "app.db"
