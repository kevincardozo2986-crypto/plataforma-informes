"""Interfaz guiada para transformar un CSV en un libro Excel."""

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QMessageBox, QProgressBar, QPushButton, QScrollArea, QVBoxLayout, QWidget,
)

from app.services.csv_service import estimate_csv_rows, inspect_csv_structure, iter_csv_chunks
from app.services.excel_service import ExcelProcess
from app.services.report_path_service import (
    copy_source_csv,
    create_report_directory,
    prepare_report_paths,
)
from app.ui.excel_preview_dialog import ExcelPreviewDialog
from app.ui.theme import EXCEL_MODULE_STYLESHEET


class BackgroundTask(QObject):
    finished = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, operation):
        super().__init__()
        self.operation = operation

    @Slot()
    def run(self):
        try:
            result = self.operation(self.progress.emit)
        except Exception as error:
            self.failed.emit(str(error))
        else:
            self.finished.emit(result)


class ProcessStepRow(QFrame):
    requested = Signal()

    def __init__(self, number, title, description, executable=True):
        super().__init__()
        self.number = number
        self.setObjectName("excelStepRow")
        self.setMinimumHeight(72)
        self.state = "pending"
        row = QHBoxLayout(self)
        row.setContentsMargins(16, 11, 16, 11)
        row.setSpacing(14)
        self.badge = QLabel(str(number))
        self.badge.setObjectName("pendingStepBadge")
        self.badge.setAlignment(Qt.AlignCenter)
        self.badge.setFixedSize(36, 36)
        copy = QVBoxLayout()
        self.title = QLabel(title)
        self.title.setObjectName("excelStepTitle")
        detail = QLabel(description)
        detail.setObjectName("excelStepDescription")
        copy.addWidget(self.title)
        copy.addWidget(detail)
        self.status = QLabel("Pendiente")
        self.status.setObjectName("pendingStepStatus")
        self.button = QPushButton("Ejecutar paso")
        self.button.setObjectName("stepActionButton")
        self.button.clicked.connect(self.requested.emit)
        self.button.setVisible(executable)
        self.button.setEnabled(False)
        self.button.setMinimumWidth(140)
        row.addWidget(self.badge)
        row.addLayout(copy, 1)
        row.addWidget(self.status)
        row.addWidget(self.button)

    def set_state(self, state, message=None):
        self.state = state
        labels = {"completed": "Completado", "available": "Disponible", "pending": "Pendiente", "error": "Error"}
        self.badge.setText(str(self.number))
        self.badge.setObjectName(f"{state}StepBadge")
        self.badge.style().unpolish(self.badge)
        self.badge.style().polish(self.badge)
        self.status.setText(message or labels[state])
        if not message:
            self.status.setText(f"●  {labels[state]}")
        self.status.setObjectName(f"{state}StepStatus")
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)
        self.button.setEnabled(state == "available")


class ExcelProcessWindow(QWidget):
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("excelProcessPage")
        self.excel_process = ExcelProcess()
        self.csv_path = None
        self.base_directory = None
        self.report_paths = None
        self.steps = []
        self._thread = None
        self._worker = None
        self.setStyleSheet(EXCEL_MODULE_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(34, 24, 34, 24)
        root.setSpacing(13)
        top = QHBoxLayout()
        back = QPushButton("←  Volver al dashboard")
        back.setObjectName("excelBackButton")
        back.clicked.connect(self.back_requested.emit)
        top.addWidget(back)
        top.addStretch()
        root.addLayout(top)
        eyebrow = QLabel("PROCESO GUIADO  •  CSV → EXCEL")
        eyebrow.setObjectName("excelEyebrow")
        title = QLabel("Generación de Excel")
        title.setObjectName("excelPageTitle")
        subtitle = QLabel("Convierte el CSV de Moodle paso a paso y revisa el resultado cuando lo necesites.")
        subtitle.setObjectName("excelPageSubtitle")

        hero = QFrame()
        hero.setObjectName("excelHero")
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 18, 24, 18)
        hero_copy = QVBoxLayout()
        hero_copy.setSpacing(6)
        hero_copy.addWidget(eyebrow)
        hero_copy.addWidget(title)
        hero_copy.addWidget(subtitle)
        hero_layout.addLayout(hero_copy, 1)
        hero_image = QLabel()
        hero_image.setObjectName("excelHeroImage")
        hero_image.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        hero_image.setPixmap(
            QPixmap(str(Path(__file__).parent / "assets" / "excel-human-hero.png")).scaled(
                410, 145, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        hero_image.setFixedSize(420, 145)
        hero_layout.addWidget(hero_image)
        root.addWidget(hero)
        root.addSpacing(5)

        root.addWidget(self._section_header(1, "Configuración del informe"))

        setup = QFrame()
        setup.setObjectName("excelSetupCard")
        grid = QGridLayout(setup)
        grid.setContentsMargins(18, 15, 18, 15)
        grid.setHorizontalSpacing(14)
        self.period = QComboBox()
        self.period.addItems(["2025-1", "2025-2", "2026-1", "2026-2"])
        self.period.setCurrentText("2026-1")
        self.level = QComboBox()
        self.level.addItems(["Pregrado", "Posgrado"])
        self.modality = QComboBox()
        self.modality.addItems(["Presencial", "Virtual", "Presencial-Virtual"])
        self.program = QComboBox()
        self.program.setEditable(True)
        self.program.addItems(["Ingeniería de Sistemas", "Ingeniería Industrial", "Administración de Empresas"])
        self.file_label = QLabel("Ningún archivo seleccionado")
        self.file_label.setObjectName("selectedCsvLabel")
        select = QPushButton("Seleccionar archivo")
        select.setObjectName("secondaryExcelButton")
        select.clicked.connect(self._select_csv)
        self.base_label = QLabel("Ninguna carpeta base seleccionada")
        self.base_label.setObjectName("selectedCsvLabel")
        select_base = QPushButton("Seleccionar carpeta base")
        select_base.setObjectName("secondaryExcelButton")
        select_base.clicked.connect(self._select_base_directory)
        self.load_button = QPushButton("Cargar CSV")
        self.load_button.setObjectName("primaryExcelButton")
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self._load_csv)
        period_label = QLabel("Periodo académico")
        period_label.setObjectName("excelFieldLabel")
        program_label = QLabel("Programa")
        program_label.setObjectName("excelFieldLabel")
        level_label = QLabel("Nivel académico")
        level_label.setObjectName("excelFieldLabel")
        modality_label = QLabel("Modalidad")
        modality_label.setObjectName("excelFieldLabel")
        base_field_label = QLabel("Carpeta base")
        base_field_label.setObjectName("excelFieldLabel")
        file_field_label = QLabel("Archivo CSV")
        file_field_label.setObjectName("excelFieldLabel")
        grid.addWidget(period_label, 0, 0)
        grid.addWidget(level_label, 0, 1)
        grid.addWidget(modality_label, 0, 2)
        grid.addWidget(program_label, 0, 3)
        grid.addWidget(self.period, 1, 0)
        grid.addWidget(self.level, 1, 1)
        grid.addWidget(self.modality, 1, 2)
        grid.addWidget(self.program, 1, 3)
        grid.addWidget(base_field_label, 2, 0, 1, 2)
        grid.addWidget(file_field_label, 2, 2, 1, 2)
        base_row = QHBoxLayout()
        base_row.addWidget(self.base_label, 1)
        base_row.addWidget(select_base)
        grid.addLayout(base_row, 3, 0, 1, 2)
        file_row = QHBoxLayout()
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(select)
        grid.addLayout(file_row, 3, 2)
        grid.addWidget(self.load_button, 3, 3)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        root.addWidget(setup)

        destination = QFrame()
        destination.setObjectName("destinationPreview")
        destination_layout = QVBoxLayout(destination)
        destination_layout.setContentsMargins(15, 10, 15, 10)
        destination_title = QLabel("Ruta institucional de destino")
        destination_title.setObjectName("destinationTitle")
        self.destination_label = QLabel("Selecciona una carpeta base para construir la ruta institucional.")
        self.destination_label.setObjectName("destinationPath")
        self.destination_label.setWordWrap(True)
        destination_header = QHBoxLayout()
        destination_number = QLabel("2")
        destination_number.setObjectName("sectionNumber")
        destination_number.setAlignment(Qt.AlignCenter)
        destination_number.setFixedSize(30, 30)
        destination_header.addWidget(destination_number)
        destination_header.addWidget(destination_title)
        destination_header.addStretch()
        destination_layout.addLayout(destination_header)
        destination_layout.addWidget(self.destination_label)
        root.addWidget(destination)

        for combo in (self.period, self.level, self.modality, self.program):
            combo.currentTextChanged.connect(self._update_destination)

        root.addWidget(self._section_header(3, "Flujo de procesamiento"))

        columns_header = QFrame()
        columns_header.setObjectName("stepsColumnsHeader")
        columns_layout = QHBoxLayout(columns_header)
        columns_layout.setContentsMargins(18, 6, 18, 6)
        step_column = QLabel("PASO")
        step_column.setFixedWidth(50)
        description_column = QLabel("DESCRIPCIÓN")
        status_column = QLabel("ESTADO")
        status_column.setFixedWidth(105)
        action_column = QLabel("ACCIÓN")
        action_column.setFixedWidth(140)
        for label in (step_column, description_column, status_column, action_column):
            label.setObjectName("stepsColumnLabel")
        columns_layout.addWidget(step_column)
        columns_layout.addWidget(description_column, 1)
        columns_layout.addWidget(status_column)
        columns_layout.addWidget(action_column)
        root.addWidget(columns_header)

        scroll = QScrollArea()
        scroll.setObjectName("excelStepsScroll")
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(176)
        steps_page = QWidget()
        steps_layout = QVBoxLayout(steps_page)
        steps_layout.setContentsMargins(0, 0, 8, 0)
        definitions = (
            ("Crear hoja Original", "Copia todos los datos del CSV sin transformarlos.", True),
            ("Convertir FechaUnix", "Agrega Fecha, Mes y Dia junto a FechaUnix en Original.", True),
        )
        for number, (name, description, executable) in enumerate(definitions, 1):
            step = ProcessStepRow(number, name, description, executable)
            self.steps.append(step)
            steps_layout.addWidget(step)
        self.steps[0].requested.connect(self._create_original)
        self.steps[1].requested.connect(self._prepare_information)
        steps_layout.addStretch()
        scroll.setWidget(steps_page)
        root.addWidget(scroll)
        root.addStretch(1)

        self.feedback = QLabel("Selecciona el periodo, el programa y un archivo CSV para comenzar.")
        self.feedback.setObjectName("excelFeedback")
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("excelProgressBar")
        self.progress_bar.setRange(1, 100)
        self.progress_bar.setValue(1)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.hide()
        actions = QHBoxLayout()
        self.preview_button = QPushButton("Previsualizar Excel")
        self.preview_button.setObjectName("secondaryExcelButton")
        self.preview_button.setEnabled(False)
        self.preview_button.clicked.connect(self._preview)
        self.save_button = QPushButton("Guardar Excel")
        self.save_button.setObjectName("primaryExcelButton")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self._save)
        status_area = QVBoxLayout()
        status_area.setSpacing(5)
        status_area.addWidget(self.feedback)
        status_area.addWidget(self.progress_bar)
        actions.addLayout(status_area, 1)
        actions.addWidget(self.preview_button)
        actions.addWidget(self.save_button)
        root.addLayout(actions)

    def _section_header(self, number, title):
        header = QFrame()
        header.setObjectName("excelSectionHeader")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        badge = QLabel(str(number))
        badge.setObjectName("sectionNumber")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(30, 30)
        label = QLabel(title)
        label.setObjectName("excelSectionTitle")
        layout.addWidget(badge)
        layout.addWidget(label, 1)
        return header

    def _select_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar CSV de Moodle", "", "Archivos CSV (*.csv)")
        if path:
            self.csv_path = path
            self.file_label.setText(Path(path).name)
            self.file_label.setToolTip(path)
            self._update_destination()

    def _select_base_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta base de informes")
        if path:
            self.base_directory = path
            self.base_label.setText(path)
            self.base_label.setToolTip(path)
            self._update_destination()

    def _update_destination(self):
        self.report_paths = None
        if not self.base_directory:
            self.destination_label.setText("Selecciona una carpeta base para construir la ruta institucional.")
            self.load_button.setEnabled(False)
            return
        try:
            source_name = self.csv_path or "Informe_Moodle.csv"
            self.report_paths = prepare_report_paths(
                self.base_directory,
                self.period.currentText(),
                self.level.currentText(),
                self.modality.currentText(),
                self.program.currentText(),
                source_name,
            )
        except ValueError as error:
            self.destination_label.setText(str(error))
            self.load_button.setEnabled(False)
            return
        self.destination_label.setText(str(self.report_paths.directory))
        self.load_button.setEnabled(bool(self.csv_path))

    def _load_csv(self):
        self._update_destination()
        if not self.report_paths or not self.csv_path:
            return
        overwrite_csv = False
        if self.report_paths.source_csv.exists():
            answer = QMessageBox.question(
                self,
                "El CSV ya existe",
                f"Ya existe {self.report_paths.source_csv.name} en la carpeta del informe.\n\n¿Deseas reemplazar la copia existente?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
            overwrite_csv = True
        paths = self.report_paths
        source_csv = self.csv_path
        self.excel_process = ExcelProcess()
        academic_data = (
            self.base_directory,
            self.period.currentText(),
            self.level.currentText(),
            self.modality.currentText(),
            self.program.currentText(),
        )
        self.steps[0].set_state("pending")
        self._start_background(
            lambda progress: self._validate_and_copy_csv(
                source_csv, paths, overwrite_csv, academic_data, progress
            ),
            self._csv_loaded,
            lambda message: self._task_failed(0, "Error al cargar el CSV", message),
        )

    def _validate_and_copy_csv(self, source_csv, paths, overwrite_csv, academic_data, progress):
        progress(10)
        columns = inspect_csv_structure(source_csv)
        progress(30)
        create_report_directory(*academic_data)
        progress(45)
        copy_source_csv(
            source_csv,
            paths.source_csv,
            overwrite=overwrite_csv,
            progress_callback=progress,
        )
        return len(columns), paths

    def _csv_loaded(self, result):
        columns, self.report_paths = result
        self.steps[0].set_state("available")
        self.steps[1].set_state("pending")
        self.preview_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.feedback.setText(
            f"CSV cargado y validado: {columns} columnas. Ejecuta el paso 1 para crear Original."
        )

    def _task_failed(self, step_index, title, message):
        self.steps[step_index].set_state("error", "No se pudo completar")
        QMessageBox.critical(self, title, message)

    def _start_background(self, operation, on_success, on_error):
        if self._thread and self._thread.isRunning():
            return
        self.load_button.setEnabled(False)
        self.preview_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.feedback.setText("Procesando el archivo por bloques. La aplicación seguirá respondiendo…")
        self.progress_bar.setValue(1)
        self.progress_bar.show()
        self._thread = QThread(self)
        self._worker = BackgroundTask(operation)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.finished.connect(on_success)
        self._worker.failed.connect(on_error)
        self._worker.finished.connect(self._finish_background)
        self._worker.failed.connect(self._finish_background)
        self._thread.start()

    @Slot()
    def _finish_background(self, *_):
        self.progress_bar.hide()
        self._thread.quit()
        self._thread.wait()
        self._worker.deleteLater()
        self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self.load_button.setEnabled(bool(self.csv_path and self.base_directory))
        available = self.excel_process.exists
        self.preview_button.setEnabled(available)
        self.save_button.setEnabled(available)

    def _prepare_information(self):
        self.steps[1].set_state("available", "Procesando…")
        self._start_background(
            lambda progress: self._write_original(prepare=True, progress=progress),
            self._information_prepared,
            lambda message: self._task_failed(1, "Error al preparar la información", message),
        )

    def _create_original(self):
        self.steps[0].set_state("available", "Procesando…")
        self._start_background(
            lambda progress: self._write_original(prepare=False, progress=progress),
            self._original_created,
            lambda message: self._task_failed(0, "Error al crear la hoja Original", message),
        )

    def _write_original(self, prepare, progress):
        progress(2)
        total_rows = estimate_csv_rows(self.csv_path)
        return self.excel_process.create_original_from_chunks(
            iter_csv_chunks(self.csv_path, prepare=prepare),
            total_rows=total_rows,
            progress_callback=progress,
        )

    def _original_created(self, result):
        rows, columns = result
        self.steps[0].set_state("completed")
        self.steps[1].set_state("available")
        self.preview_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.feedback.setText(
            f"Hoja Original creada: {rows:,} registros y {columns} columnas."
        )

    def _information_prepared(self, result):
        rows, columns = result
        self.steps[1].set_state("completed")
        self.preview_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.feedback.setText(
            f"FechaUnix convertida: se actualizaron {rows:,} registros en la hoja Original."
        )

    def _preview(self):
        ExcelPreviewDialog(self.excel_process, self).exec()

    def _save(self):
        if not self.report_paths:
            return
        destination = self.report_paths.excel
        if destination.exists():
            answer = QMessageBox.question(
                self,
                "El Excel ya existe",
                f"Ya existe {destination.name}.\n\n¿Deseas reemplazarlo?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if answer != QMessageBox.Yes:
                return
        try:
            self.excel_process.save_as(destination)
        except OSError as error:
            QMessageBox.critical(self, "No se pudo guardar", str(error))
            return
        self.feedback.setText(f"Excel guardado en {destination}")
        QMessageBox.information(self, "Excel guardado", "El archivo se guardó correctamente.")
