"""Modulo independiente para convertir un Excel terminado en informe Word."""

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QProgressBar, QPushButton, QVBoxLayout, QWidget,
)

from app.services.report_option_service import list_report_options
from app.services.report_path_service import build_word_path
from app.services.process_history_service import list_completed_processes
from app.services.word_report_service import generate_word_report
from app.ui.modal_dialogs import ask_confirmation, show_error, show_info
from app.ui.theme import EXCEL_MODULE_STYLESHEET


class WordGenerationTask(QObject):
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, operation):
        super().__init__()
        self.operation = operation

    @Slot()
    def run(self):
        try:
            result = self.operation()
        except Exception as error:
            self.failed.emit(str(error))
        else:
            self.finished.emit(result)


class WordReportWindow(QWidget):
    back_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setObjectName("excelProcessPage")
        self.setStyleSheet(EXCEL_MODULE_STYLESHEET)
        self.excel_path = None
        self.generated_path = None
        self._thread = None
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 24, 34, 24)
        root.setSpacing(16)

        back = QPushButton("←  Volver al dashboard")
        back.setObjectName("excelBackButton")
        back.setFixedWidth(200)
        back.clicked.connect(self.back_requested.emit)
        top = QHBoxLayout()
        top.addWidget(back)
        top.addStretch()
        root.addLayout(top)

        hero = QFrame()
        hero.setObjectName("excelHero")
        hero.setStyleSheet("QFrame#excelHero { background-color: #FAFBFD; border-radius: 12px; }")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 26, 28, 26)
        hero_layout.setSpacing(6)
        eyebrow = QLabel("GENERADOR DE INFORMES  •  EXCEL → WORD")
        eyebrow.setObjectName("excelEyebrow")
        eyebrow.setStyleSheet("color: #FF5E70; font-size: 9px; font-weight: 900; letter-spacing: 2px;")
        title = QLabel("Crear informe institucional")
        title.setObjectName("excelPageTitle")
        title.setStyleSheet("color: #071D38; font-size: 32px; font-weight: 800;")
        subtitle = QLabel(
            "Transforma tus datos en un documento profesional Word listo para presentar."
        )
        subtitle.setObjectName("excelPageSubtitle")
        subtitle.setStyleSheet("color: #687086; font-size: 13px; line-height: 1.5;")
        subtitle.setWordWrap(True)
        hero_layout.addWidget(eyebrow)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        root.addWidget(hero)

        card = QFrame()
        card.setObjectName("sourceFilesPanel")
        card.setStyleSheet("QFrame#sourceFilesPanel { background-color: #FFFFFF; border: 1px solid #E3E6ED; border-radius: 12px; }")
        grid = QGridLayout(card)
        grid.setContentsMargins(28, 26, 28, 26)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(14)

        completed_title = QLabel("📋  Informes disponibles")
        completed_title.setObjectName("excelFieldLabel")
        completed_title.setStyleSheet("color: #123D68; font-size: 13px; font-weight: 700;")
        self.completed_reports = QComboBox()
        self.completed_reports.setStyleSheet("QComboBox { padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-size: 12px; }")
        self.completed_reports.currentIndexChanged.connect(
            self._select_completed_report
        )
        refresh = QPushButton("🔄 Actualizar")
        refresh.setObjectName("secondaryExcelButton")
        refresh.setStyleSheet("QPushButton { background-color: #FFFFFF; color: #211568; border: 1px solid #D9DDE7; border-radius: 6px; padding: 8px 14px; font-size: 12px; font-weight: 600; }")
        refresh.clicked.connect(self._load_completed_reports)

        excel_title = QLabel("📁  Archivo Excel")
        excel_title.setObjectName("excelFieldLabel")
        excel_title.setStyleSheet("color: #123D68; font-size: 13px; font-weight: 700;")
        self.file_label = QLabel("Sin archivo seleccionado")
        self.file_label.setObjectName("selectedCsvLabel")
        self.file_label.setStyleSheet("background-color: #F5F7FB; color: #687086; border-radius: 6px; padding: 10px 12px; font-size: 11px; border-left: 3px solid #36BCE8;")
        self.file_label.setWordWrap(True)
        browse = QPushButton("📂 Seleccionar Excel")
        browse.setObjectName("secondaryExcelButton")
        browse.setStyleSheet("QPushButton { background-color: #36BCE8; color: white; border: none; border-radius: 6px; padding: 8px 14px; font-size: 12px; font-weight: 600; }")
        browse.clicked.connect(self._select_excel)

        period_title = QLabel("📅  Periodo")
        period_title.setObjectName("excelFieldLabel")
        period_title.setStyleSheet("color: #123D68; font-size: 13px; font-weight: 700;")
        self.period = QComboBox()
        self.period.setStyleSheet("QComboBox { padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-size: 12px; }")
        self.period.addItems(list_report_options("period"))
        program_title = QLabel("🎓  Programa")
        program_title.setObjectName("excelFieldLabel")
        program_title.setStyleSheet("color: #123D68; font-size: 13px; font-weight: 700;")
        self.program = QComboBox()
        self.program.setStyleSheet("QComboBox { padding: 8px 12px; border-radius: 6px; border: 1px solid #CBD5E1; font-size: 12px; }")
        self.program.addItems(list_report_options("program"))

        grid.addWidget(completed_title, 0, 0, 1, 2)
        grid.addWidget(self.completed_reports, 1, 0)
        grid.addWidget(refresh, 1, 1)
        grid.addWidget(excel_title, 2, 0, 1, 2)
        grid.addWidget(self.file_label, 3, 0, 1, 2)
        grid.addWidget(browse, 4, 0, 1, 2)
        grid.addWidget(period_title, 5, 0)
        grid.addWidget(self.period, 6, 0)
        grid.addWidget(program_title, 5, 1)
        grid.addWidget(self.program, 6, 1)

        output_title = QLabel("📄  Documento de salida")
        output_title.setObjectName("destinationTitle")
        output_title.setStyleSheet("color: #123D68; font-size: 13px; font-weight: 700;")
        self.output_label = QLabel("Selecciona un Excel para ver la ruta de destino.")
        self.output_label.setObjectName("destinationPath")
        self.output_label.setStyleSheet("background-color: #F0F7FF; color: #3B5998; border-radius: 6px; padding: 10px 12px; font-size: 11px; border-left: 3px solid #0A4D91;")
        self.output_label.setWordWrap(True)
        grid.addWidget(output_title, 7, 0, 1, 2)
        grid.addWidget(self.output_label, 8, 0, 1, 2)
        root.addWidget(card)

        self.feedback = QLabel(
            "ℹ️ El Excel debe contener 'Resumen Informe' y las hojas gráficas completadas."
        )
        self.feedback.setObjectName("excelFeedback")
        self.feedback.setStyleSheet("color: #687086; font-size: 12px; background-color: #F5F7FB; padding: 10px 12px; border-radius: 6px; border-left: 3px solid #36BCE8;")
        self.feedback.setWordWrap(True)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #E8EDF3;
                border-radius: 6px;
                height: 8px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #36BCE8;
                border-radius: 6px;
            }
        """)
        self.progress.hide()
        self.generate_button = QPushButton("⚙️ Generar informe Word")
        self.generate_button.setObjectName("primaryExcelButton")
        self.generate_button.setStyleSheet("""
            QPushButton {
                background-color: #FF5E70;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 18px;
                font-size: 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #EB4B5E;
            }
            QPushButton:pressed {
                background-color: #D93F52;
            }
            QPushButton:disabled {
                background-color: #D9DDE7;
                color: #99A0AC;
            }
        """)
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self._generate)
        actions = QHBoxLayout()
        actions.setSpacing(12)
        actions.addWidget(self.feedback, 1)
        actions.addWidget(self.progress)
        actions.addWidget(self.generate_button)
        root.addLayout(actions)
        root.addStretch()

        self.period.currentTextChanged.connect(self._update_output)
        self.program.currentTextChanged.connect(self._update_output)
        self._load_completed_reports()

    def reset(self):
        self.excel_path = None
        self.generated_path = None
        self.file_label.setText("Ningun archivo seleccionado")
        self.output_label.setText("Selecciona un Excel para calcular la ruta del Word.")
        self.generate_button.setEnabled(False)
        self._load_completed_reports()

    def _load_completed_reports(self):
        reports = list_completed_processes(self.user)
        available = [
            report for report in reports
            if Path(report["workbook_path"]).is_file()
        ]
        self.completed_reports.blockSignals(True)
        self.completed_reports.clear()
        if available:
            for report in available:
                owner = report.get("owner_name") or "Usuario"
                label = (
                    f'{report["period"]}  •  {report["program"]}  •  {owner}'
                )
                self.completed_reports.addItem(label, report)
        else:
            self.completed_reports.addItem("✗ No hay Excel terminados disponibles", None)
        self.completed_reports.blockSignals(False)
        self.completed_reports.setEnabled(bool(available))
        if available:
            self.completed_reports.setCurrentIndex(0)
            self._select_completed_report(0)
            self.feedback.setText(
                f"✓ {len(available)} Excel terminado(s) disponible(s) listo(s) para convertir."
            )
        else:
            self.feedback.setText(
                "ℹ️ No hay Excel terminados en el sistema. Puedes seleccionar uno manualmente desde tu computadora."
            )

    def _select_completed_report(self, index):
        report = self.completed_reports.itemData(index)
        if not report:
            self.feedback.setText("⚠️ Por favor selecciona un archivo válido.")
            return
        self.excel_path = Path(report["workbook_path"])
        filename = self.excel_path.name
        self.file_label.setText(f"✓ {filename}")
        self.file_label.setToolTip(str(self.excel_path))
        for combo, value in (
            (self.period, report["period"]),
            (self.program, report["program"]),
        ):
            if combo.findText(value) < 0:
                combo.addItem(value)
            combo.setCurrentText(value)
        self.generate_button.setEnabled(True)
        self.feedback.setText(f"✓ Archivo: {filename} (listo para generar)")
        self._update_output()

    def _select_excel(self):
        selected, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Excel terminado", "", "Archivos Excel (*.xlsx)"
        )
        if not selected:
            return
        self.completed_reports.blockSignals(True)
        self.completed_reports.setCurrentIndex(-1)
        self.completed_reports.blockSignals(False)
        self.excel_path = Path(selected)
        filename = self.excel_path.name
        self.file_label.setText(f"✓ {filename}")
        self.file_label.setToolTip(str(self.excel_path))
        self.generate_button.setEnabled(True)
        self.feedback.setText(f"✓ {filename} cargado. Verifica período y programa antes de generar.")
        self._update_output()

    def _destination(self):
        if not self.excel_path:
            return None
        return build_word_path(
            self.excel_path.parent,
            self.period.currentText(),
            self.program.currentText(),
        )

    def _update_output(self):
        destination = self._destination()
        if destination:
            self.output_label.setText(f"📍 {destination.name}")
            self.output_label.setToolTip(str(destination))

    def _generate(self):
        destination = self._destination()
        if not destination:
            return
        if destination.exists() and not ask_confirmation(
            self,
            "El informe ya existe",
            f"Ya existe {destination.name}.\n\n\u00bfDeseas reemplazarlo?",
        ):
            return
        program = self.program.currentText()
        period = self.period.currentText()
        excel_path = self.excel_path
        self.generate_button.setEnabled(False)
        self.progress.show()
        self.feedback.setText("⏳ Generando informe... (extrayendo datos, creando gráficos y tablas)")
        self.feedback.setStyleSheet("color: #FF5E70; font-size: 12px; background-color: #FFF0F3; padding: 10px 12px; border-radius: 6px; border-left: 3px solid #FF5E70; font-weight: 600;")
        self._thread = QThread(self)
        self._worker = WordGenerationTask(
            lambda: generate_word_report(
                excel_path, destination, program, period
            )
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._generated)
        self._worker.failed.connect(self._failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.failed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread_finished)
        self._thread.start()

    def _generated(self, path):
        self.generated_path = Path(path)
        self.feedback.setText(f"✓ ¡Informe generado exitosamente! → {Path(path).name}")
        self.feedback.setStyleSheet("color: #0A7F4E; font-size: 12px; background-color: #E8F5E9; padding: 10px 12px; border-radius: 6px; border-left: 3px solid #4CAF50; font-weight: 600;")
        show_info(
            self, "¡Informe generado!",
            f"El documento Word se creó correctamente.\n\n📄 {Path(path).name}", success=True,
        )

    def _failed(self, message):
        self.feedback.setText("✗ Error al generar el informe. Ver detalles abajo.")
        self.feedback.setStyleSheet("color: #C53E56; font-size: 12px; background-color: #FFF0F3; padding: 10px 12px; border-radius: 6px; border-left: 3px solid #FF5E70; font-weight: 600;")
        show_error(self, "❌ Error al generar el Word", message)

    @Slot()
    def _thread_finished(self):
        thread = self._thread
        self._worker = None
        self._thread = None
        if thread:
            thread.deleteLater()
        self.progress.hide()
        self.generate_button.setEnabled(bool(self.excel_path))
