"""Comprobación explícita del ejecutable, sin acceder a datos del usuario."""
import json
from pathlib import Path


def run(result_path):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPixmap
    from docx import Document
    import docx2pdf
    from app.database.database import DATABASE_PATH
    from app.services.auth_service import initialize_database
    from app.services.word_report_service import _bundled_template_path
    from app.ui.login_window import LoginWindow

    app = QApplication.instance() or QApplication([])
    assets = Path(__file__).parent / "ui" / "assets"
    assert not QPixmap(str(assets / "usta-crest.png")).isNull()
    assert not QPixmap(str(assets / "home.svg")).isNull()
    assert (assets / "manual-usuario.pdf").read_bytes().startswith(b"%PDF")
    assert Document(_bundled_template_path()).tables
    assert (Path(docx2pdf.__file__).parent / "convert.jxa").is_file()
    initialize_database()
    window = LoginWindow()
    window.show()
    app.processEvents()
    window.close()
    Path(result_path).write_text(json.dumps({"ok": True, "database": str(DATABASE_PATH)}), encoding="utf-8")
