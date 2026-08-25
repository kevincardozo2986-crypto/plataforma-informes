"""Vista previa ligera del libro Excel sin abrir aplicaciones externas."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from app.ui.theme import EXCEL_MODULE_STYLESHEET
from app.ui.window_chrome import preparar_ventana_sin_marco


class ExcelPreviewDialog(QDialog):
    def __init__(self, proceso_excel, ventana_padre=None):
        super().__init__(ventana_padre)
        self.proceso_excel = proceso_excel
        self.setWindowTitle("Vista previa del Excel")
        self.resize(1050, 650)
        self.setObjectName("excelPreviewDialog")
        self.setStyleSheet(EXCEL_MODULE_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        diseno = QVBoxLayout(self)
        diseno.setContentsMargins(0, 0, 0, 0)
        diseno.setSpacing(0)
        diseno.addWidget(
            preparar_ventana_sin_marco(
                self, "Vista previa del Excel", controles_completos=True
            )
        )
        contenido = QVBoxLayout()
        contenido.setContentsMargins(24, 22, 24, 20)
        titulo = QLabel("Vista previa del Excel")
        titulo.setObjectName("excelPageTitle")
        subtitulo = QLabel("Se muestran como máximo 75 registros por hoja; el archivo conserva todos los datos.")
        subtitulo.setObjectName("excelPageSubtitle")
        self.pestanas = QTabWidget()
        self.pestanas.setObjectName("previewTabs")
        contenido.addWidget(titulo)
        contenido.addWidget(subtitulo)
        contenido.addSpacing(10)
        contenido.addWidget(self.pestanas, 1)

        for nombre_hoja in self.proceso_excel.sheet_names():
            self.pestanas.addTab(self._create_sheet_tab(nombre_hoja), nombre_hoja)

        acciones = QHBoxLayout()
        acciones.addStretch()
        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.setObjectName("secondaryExcelButton")
        boton_cerrar.clicked.connect(self.accept)
        acciones.addWidget(boton_cerrar)
        contenido.addLayout(acciones)
        diseno.addLayout(contenido, 1)

    def _create_sheet_tab(self, nombre_hoja):
        pagina = QWidget()
        diseno = QVBoxLayout(pagina)
        encabezados, filas, total_filas = self.proceso_excel.preview_sheet(nombre_hoja, limit=75)
        informacion = QLabel(f"Mostrando {len(filas):,} de {total_filas:,} registros")
        informacion.setObjectName("previewInfo")
        tabla = QTableWidget(len(filas), len(encabezados))
        tabla.setObjectName("excelPreviewTable")
        tabla.setHorizontalHeaderLabels(encabezados)
        tabla.setAlternatingRowColors(True)
        tabla.setEditTriggers(QTableWidget.NoEditTriggers)
        tabla.setSelectionBehavior(QTableWidget.SelectRows)
        for indice_fila, fila in enumerate(filas):
            for indice_columna, valor in enumerate(fila):
                celda = QTableWidgetItem("" if valor is None else str(valor))
                celda.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                tabla.setItem(indice_fila, indice_columna, celda)
        tabla.resizeColumnsToContents()
        diseno.addWidget(informacion)
        diseno.addWidget(tabla, 1)
        return pagina
