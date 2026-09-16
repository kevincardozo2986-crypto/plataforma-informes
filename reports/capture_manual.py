"""Capturas de la interfaz con datos de demostración, sin consultar la base real."""
from pathlib import Path
from unittest.mock import MagicMock, patch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from app.ui.dashboard_window import DashboardWindow
from app.ui.history_page import HistoryPage
from app.ui.theme import DASHBOARD_STYLESHEET

app = QApplication([])
for font in ('segoeui.ttf', 'segoeuib.ttf', 'seguisb.ttf'):
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/' + font)
app.setFont(QFont('Segoe UI', 10))

class Preview:
    user = {'role': 'admin', 'full_name': 'Cuenta de demostración'}
    _create_sidebar = DashboardWindow._create_sidebar
    _create_content = DashboardWindow._create_content
    _nav = DashboardWindow._nav

    def __getattr__(self, key):
        return MagicMock()

home = DashboardWindow._create_home_page(Preview())
home.setStyleSheet(DASHBOARD_STYLESHEET + home.styleSheet())
home.resize(1440, 900)
home.show()
app.processEvents()
home.grab().save('reports/manual-home.png')
home.close()
record = {'program': 'Programa de demostración A', 'period': '2026-1', 'status': 'completed',
          'workbook_path': 'Informe_ejemplo.xlsx', 'updated_at': '2026-09-15 10:00'}
with patch('app.ui.history_page.list_completed_processes', return_value=[record]), patch(
    'app.ui.history_page.list_incomplete_processes', return_value=[dict(record, program='Programa de demostración B', status='in_progress')]
):
    history = HistoryPage(Preview.user)
    history.refresh()
    history.resize(1440, 900)
    history.show()
    app.processEvents()
    history.grab().save('reports/manual-history.png')
    history.close()
print('Capturas listas: inicio e historial con datos de demostración.')
