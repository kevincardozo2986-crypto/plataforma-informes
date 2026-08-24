"""Vista previa ligera del libro Excel sin abrir aplicaciones externas."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from app.ui.theme import EXCEL_MODULE_STYLESHEET


class ExcelPreviewDialog(QDialog):
    def __init__(self, excel_process, parent=None):
        super().__init__(parent)
        self.excel_process = excel_process
        self.setWindowTitle("Vista previa del Excel")
        self.resize(1050, 650)
        self.setObjectName("excelPreviewDialog")
        self.setStyleSheet(EXCEL_MODULE_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 20)
        title = QLabel("Vista previa del Excel")
        title.setObjectName("excelPageTitle")
        subtitle = QLabel("Se muestran como máximo 75 registros por hoja; el archivo conserva todos los datos.")
        subtitle.setObjectName("excelPageSubtitle")
        self.tabs = QTabWidget()
        self.tabs.setObjectName("previewTabs")
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(10)
        layout.addWidget(self.tabs, 1)

        for sheet_name in self.excel_process.sheet_names():
            self.tabs.addTab(self._create_sheet_tab(sheet_name), sheet_name)

        actions = QHBoxLayout()
        actions.addStretch()
        close_button = QPushButton("Cerrar")
        close_button.setObjectName("secondaryExcelButton")
        close_button.clicked.connect(self.accept)
        actions.addWidget(close_button)
        layout.addLayout(actions)

    def _create_sheet_tab(self, sheet_name):
        page = QWidget()
        layout = QVBoxLayout(page)
        headers, rows, total_rows = self.excel_process.preview_sheet(sheet_name, limit=75)
        info = QLabel(f"Mostrando {len(rows):,} de {total_rows:,} registros")
        info.setObjectName("previewInfo")
        table = QTableWidget(len(rows), len(headers))
        table.setObjectName("excelPreviewTable")
        table.setHorizontalHeaderLabels(headers)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                table.setItem(row_index, column_index, item)
        table.resizeColumnsToContents()
        layout.addWidget(info)
        layout.addWidget(table, 1)
        return page
