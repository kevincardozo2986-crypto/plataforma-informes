"""Explorador interactivo para convertir Excel terminados en informes Word."""

from pathlib import Path
import re

from openpyxl import load_workbook
from PySide6.QtCore import QObject, QSize, QThread, Qt, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QDesktopServices, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QProgressBar, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from app.services.report_option_service import list_report_options
from app.services.report_path_service import build_pdf_path, build_word_path
from app.services.pdf_report_service import convert_word_to_pdf
from app.services.process_history_service import list_completed_processes
from app.services.word_report_service import generate_word_report
from app.ui.assistant import anchor_bottom_right
from app.ui.modal_dialogs import ask_confirmation, show_error, show_info
from app.ui.theme import EXCEL_MODULE_STYLESHEET


WORD_STYLE = EXCEL_MODULE_STYLESHEET + """
QWidget#excelProcessPage QLabel, QWidget#excelProcessPage QPushButton, QWidget#excelProcessPage QLineEdit, QWidget#excelProcessPage QComboBox, QWidget#excelProcessPage QListWidget { font-family: "Segoe UI"; }
QFrame#wordHero { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #092C53, stop:1 #14569A); border: none; border-radius: 18px; }
QLabel#wordHeroImage { background: transparent; border: none; }
QLabel#wordEyebrow { color: #F4CE67; font-size: 10px; font-weight: 600; letter-spacing: 1px; }
QLabel#wordTitle { color: #FFFFFF; font-size: 28px; font-weight: 700; }
QLabel#wordSubtitle { color: #D9E7F6; font-size: 13px; }
QLabel#wordStepNumber { color: #183455; background-color: #F4CE67; border-radius: 10px; font-size: 10px; font-weight: 700; }
QLabel#wordStepText { color: #E5EFF9; font-size: 11px; font-weight: 600; }
QLabel#wordStepArrow { color: #78CDEB; font-size: 11px; }
QFrame#wordPanel { background-color: #FFFFFF; border: 1px solid #D9E2EC; border-radius: 14px; }
QLabel#wordSection { color: #102A49; font-size: 16px; font-weight: 800; }
QLabel#wordPanelHint { color: #617185; font-size: 12px; }
QLabel#wordMuted { color: #718096; font-size: 10px; }
QLineEdit#reportSearch, QComboBox#reportFilter {
    background-color: #F8FAFC; color: #173653; border: 1px solid #D3DDE8;
    border-radius: 9px; padding: 9px 12px; min-height: 22px;
}
QLineEdit#reportSearch:focus, QComboBox#reportFilter:focus { border: 2px solid #0B67D1; }
QComboBox#reportFilter { color: #42566D; font-weight: 500; background-color: #FFFFFF; }
QListWidget#reportList { background: #FFFFFF; border: none; padding: 0px; outline: 0; font-size: 13px; }
QListWidget#reportList::item { color: #173653; background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 6px; padding: 8px; margin: 0px 0px 6px 0px; }
QListWidget#reportList::item:hover { border-color: #83B8EA; background: #F3F8FE; }
QListWidget#reportList::item:selected { color: #073A6F; border: 1px solid #9CBADD; background: #EDF4FC; }
QLabel#countBadge { color: #075EAE; background: #E5F2FF; border-radius: 10px; padding: 4px 9px; font-weight: 800; }
QLabel#selectionTitle { color: #0B315A; font-size: 20px; font-weight: 700; padding: 10px 12px; background: #F0F5FC; border-left: 3px solid #D5AB39; border-radius: 4px; }
QLabel#selectionBadge { color: #137346; background-color: #E3F4EA; border-radius: 10px; padding: 5px 10px; font-size: 9px; font-weight: 900; }
QLabel#detailLabel { color: #64748B; font-size: 10px; font-weight: 700; }
QLabel#detailValue { color: #183455; font-size: 13px; background: transparent; border: none; padding: 0px 0px 6px 0px; }
QFrame#wordActionArea { background-color: #F7F9FC; border: none; border-radius: 8px; }
QLabel#excelFeedback { background: transparent; border: none; padding: 4px 0px; color: #53677D; font-size: 12px; }
QPushButton#wordPrimary { background: #0B67D1; color: white; border: none; border-radius: 9px; padding: 12px 18px; font-size: 12px; font-weight: 900; }
QPushButton#wordPrimary:hover { background: #0959B7; }
QPushButton#wordPrimary:disabled { background: #D8E0E9; color: #929EAC; }
QPushButton#wordAction { background: #FFFFFF; color: #0B5DAC; border: 1px solid #B7CCE1; border-radius: 8px; padding: 9px 14px; font-weight: 800; }
QPushButton#wordAction:hover { background: #EDF6FF; }
QPushButton#wordPdfAction { background: #C62828; color: #FFFFFF; border: 1px solid #C62828; border-radius: 8px; padding: 9px 14px; font-size: 12px; font-weight: 700; }
QPushButton#wordPdfAction:hover { background: #B71C1C; border-color: #B71C1C; }
QPushButton#wordPdfAction:pressed { background: #991B1B; border-color: #991B1B; }
QPushButton#wordPdfAction:disabled { background: #F3DADA; color: #886767; border-color: #E9CCCC; }
QPushButton#wordPdfAction:focus { border: 2px solid #F59E9E; }
QPushButton#wordSelectAction { background: #FFFFFF; color: #0B5DAC; border: 1px solid #B7CCE1; border-radius: 8px; padding: 9px 14px; font-weight: 600; }
QPushButton#wordSelectAction:hover { background: #EDF6FF; }
"""


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
        except BaseException as error:  # noqa: BLE001 - debe mostrarse, no tumbar la app
            self.failed.emit(f"{type(error).__name__}: {error}")
        else:
            self.finished.emit(result)


class WordReportWindow(QWidget):
    back_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setObjectName("excelProcessPage")
        self.setStyleSheet(WORD_STYLE)
        self.reports = []
        self.excel_path = None
        self.generated_path = None
        self.generated_pdf_path = None
        self.current_program = ""
        self.current_period = ""
        self._thread = None
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 14, 24, 16)
        root.setSpacing(14)
        navigation = QHBoxLayout()
        back = QPushButton("←  Volver al dashboard", objectName="excelBackButton")
        back.clicked.connect(self.back_requested.emit)
        navigation.addWidget(back)
        navigation.addStretch()
        navigation.addWidget(QLabel("PLATAFORMA DE INFORMES  ·  Santoto Tunja", objectName="wordMuted"))
        root.addLayout(navigation)

        hero = QFrame(objectName="wordHero")
        hero_box = QHBoxLayout(hero)
        hero_box.setContentsMargins(24, 18, 24, 18)
        hero_box.setSpacing(12)
        hero_copy = QVBoxLayout()
        hero_copy.setSpacing(8)
        eyebrow = QLabel("INFORMES  /  GENERACIÓN DE DOCUMENTOS", objectName="wordEyebrow")
        title = QLabel("Generar informe Word", objectName="wordTitle")
        for label in (eyebrow, title):
            label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        hero_copy.addWidget(eyebrow)
        hero_copy.addWidget(title)
        subtitle = QLabel("Selecciona un Excel y crea tu informe con la plantilla institucional.", objectName="wordSubtitle")
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        hero_copy.addWidget(subtitle)
        steps = QHBoxLayout()
        steps.setSpacing(7)
        for index, step_text in enumerate(("Seleccionar", "Revisar", "Generar"), 1):
            number = QLabel(str(index), objectName="wordStepNumber")
            number.setAlignment(Qt.AlignCenter)
            number.setFixedSize(20, 20)
            steps.addWidget(number)
            steps.addWidget(QLabel(step_text, objectName="wordStepText"))
            if index < 3:
                steps.addWidget(QLabel(">", objectName="wordStepArrow"))
        steps.addStretch()
        hero_copy.addLayout(steps)
        hero_box.addLayout(hero_copy, 4)
        # Reserve a dedicated area for Tomy so his bubble never covers controls.
        hero_box.addSpacing(290)
        hero.setMinimumHeight(164)
        self._mascot_buddy = anchor_bottom_right(hero, "word")
        root.addWidget(hero)

        content = QHBoxLayout()
        content.setSpacing(13)
        root.addLayout(content, 1)
        explorer = QFrame(objectName="wordPanel")
        left = QVBoxLayout(explorer)
        left.setContentsMargins(18, 16, 18, 16)
        left.setSpacing(10)
        heading = QHBoxLayout()
        heading.addWidget(QLabel("Archivos disponibles", objectName="wordSection"))
        self.count_badge = QLabel("0 disponibles", objectName="countBadge")
        heading.addStretch()
        heading.addWidget(self.count_badge)
        left.addLayout(heading)
        explorer_hint = QLabel("Encuentra un proceso finalizado usando el buscador o los filtros.", objectName="wordPanelHint")
        explorer_hint.setWordWrap(True)
        left.addWidget(explorer_hint)
        self.search = QLineEdit(objectName="reportSearch")
        self.search.setPlaceholderText("Buscar por nombre, programa o periodo...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._apply_filters)
        left.addWidget(self.search)

        filters = QHBoxLayout()
        self.period_filter = QComboBox(objectName="reportFilter")
        self.program_filter = QComboBox(objectName="reportFilter")
        for combo in (self.period_filter, self.program_filter):
            combo.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
            combo.setMinimumContentsLength(10)
            combo.currentTextChanged.connect(self._apply_filters)
            filters.addWidget(combo, 1)
        left.addLayout(filters)
        self.report_list = QListWidget(objectName="reportList")
        self.report_list.setMinimumWidth(360)
        self.report_list.currentItemChanged.connect(self._report_selected)
        self.report_list.itemDoubleClicked.connect(lambda _: self._generate())
        left.addWidget(self.report_list, 1)
        list_actions = QHBoxLayout()
        refresh = QPushButton("Actualizar", objectName="wordAction")
        refresh.clicked.connect(self._load_completed_reports)
        browse = QPushButton("+  Seleccionar otro Excel", objectName="wordSelectAction")
        browse.clicked.connect(self._select_excel)
        list_actions.addWidget(refresh)
        list_actions.addWidget(browse)
        left.addLayout(list_actions)
        content.addWidget(explorer, 3)

        details = QFrame(objectName="wordPanel")
        right = QVBoxLayout(details)
        right.setContentsMargins(20, 16, 20, 16)
        right.setSpacing(8)
        detail_heading = QHBoxLayout()
        detail_heading.addWidget(QLabel("Resumen del documento", objectName="wordSection"))
        detail_heading.addStretch()
        self.selection_badge = QLabel("SIN SELECCIÓN", objectName="selectionBadge")
        detail_heading.addWidget(self.selection_badge)
        right.addLayout(detail_heading)
        preview_hint = QLabel("Confirma la información que se insertará en la plantilla institucional.", objectName="wordPanelHint")
        preview_hint.setWordWrap(True)
        right.addWidget(preview_hint)
        self.selection_title = QLabel("Selecciona un Excel", objectName="selectionTitle")
        self.selection_title.setWordWrap(True)
        right.addWidget(self.selection_title)
        self.detail_values = {}
        detail_grid = QGridLayout()
        detail_grid.setVerticalSpacing(5)
        detail_grid.setHorizontalSpacing(20)
        detail_grid.setColumnStretch(0, 1)
        detail_grid.setColumnStretch(1, 1)
        fields = (("program", "PROGRAMA"), ("period", "PERIODO"), ("events", "EVENTOS REGISTRADOS"), ("file", "ARCHIVO DE ORIGEN"), ("output", "DOCUMENTO DE SALIDA"))
        positions = ((0, 0, 2), (2, 0, 1), (2, 1, 1), (4, 0, 2), (6, 0, 2))
        for (key, label), (row, column, span) in zip(fields, positions):
            detail_grid.addWidget(QLabel(label, objectName="detailLabel"), row, column, 1, span)
            value = QLabel("-", objectName="detailValue")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value.setMinimumWidth(0)
            value.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            self.detail_values[key] = value
            detail_grid.addWidget(value, row + 1, column, 1, span)
        right.addLayout(detail_grid)
        right.addStretch()
        action_area = QFrame(objectName="wordActionArea")
        action_box = QVBoxLayout(action_area)
        action_box.setContentsMargins(12, 11, 12, 12)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        action_box.addWidget(self.progress)
        self.feedback = QLabel("Selecciona un Excel terminado para continuar.", objectName="excelFeedback")
        self.feedback.setWordWrap(True)
        action_box.addWidget(self.feedback)
        self.generate_button = QPushButton("Crear documento Word  →", objectName="wordPrimary")
        self.generate_button.setEnabled(False)
        self.generate_button.clicked.connect(self._generate)
        action_box.addWidget(self.generate_button)
        generated_actions = QHBoxLayout()
        self.open_button = QPushButton("Abrir Word", objectName="wordAction")
        self.pdf_button = QPushButton("Generar PDF", objectName="wordPdfAction")
        self.pdf_button.setIcon(QIcon(str(Path(__file__).parent / "assets" / "pdf.svg")))
        self.pdf_button.setIconSize(QSize(24, 24))
        self.pdf_button.setCursor(Qt.PointingHandCursor)
        self.open_button.clicked.connect(self._open_generated)
        self.pdf_button.clicked.connect(self._generate_pdf)
        self.open_button.hide()
        self.pdf_button.hide()
        generated_actions.addWidget(self.open_button)
        generated_actions.addWidget(self.pdf_button)
        action_box.addLayout(generated_actions)
        right.addWidget(action_area)
        content.addWidget(details, 2)
        self._load_completed_reports()

    def reset(self):
        if self._thread is not None:
            return
        self.search.clear()
        self.generated_path = None
        self.generated_pdf_path = None
        self.open_button.hide()
        self.pdf_button.hide()
        self._load_completed_reports()

    def _load_completed_reports(self, *_):
        if self._thread is not None:
            return
        self.reports = [r for r in list_completed_processes(self.user) if Path(r["workbook_path"]).is_file()]
        self._populate_filter(self.period_filter, "Todos los periodos", "period")
        self._populate_filter(self.program_filter, "Todos los programas", "program")
        self._apply_filters()

    def _populate_filter(self, combo, all_text, key):
        current = combo.currentText()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem(all_text, None)
        for value in sorted({str(r.get(key) or "Usuario") for r in self.reports}):
            combo.addItem(value, value)
        index = combo.findText(current)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.blockSignals(False)

    def _excel_icon(self):
        """Crea un icono verde tipo Excel sin depender de un SVG externo."""
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hoja/documento
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#EAF6EF"))
        painter.drawRoundedRect(4, 2, 24, 28, 5, 5)

        # Franja Excel
        painter.setBrush(QColor("#107C41"))
        painter.drawRoundedRect(3, 7, 20, 19, 4, 4)

        # Letra X
        painter.setPen(QColor("#FFFFFF"))
        font = QFont()
        font.setBold(True)
        font.setPointSize(11)
        painter.setFont(font)
        painter.drawText(3, 7, 20, 19, Qt.AlignCenter, "X")

        painter.end()
        return QIcon(pixmap)

    def _apply_filters(self, *_):
        query = self.search.text().strip().casefold()
        period, program = self.period_filter.currentData(), self.program_filter.currentData()
        filtered = []
        for report in self.reports:
            haystack = " ".join(str(report.get(k) or "") for k in ("workbook_path", "period", "program", "level", "modality")).casefold()
            if query and query not in haystack:
                continue
            if period and report.get("period") != period:
                continue
            if program and report.get("program") != program:
                continue
            filtered.append(report)
        self.report_list.clear()
        for report in filtered:
            path = Path(report["workbook_path"])
            context = "  |  ".join(
                value for value in (
                    str(report.get("period") or ""),
                    str(report.get("level") or ""),
                    str(report.get("modality") or ""),
                ) if value
            )
            text = f'{report.get("program", "Sin programa")}\n{context}'
            item = QListWidgetItem(text)
            item.setToolTip(f'{text}\n{path.name}')
            item.setIcon(self._excel_icon())
            item.setData(Qt.UserRole, report)
            item.setSizeHint(QSize(0, 72))
            self.report_list.addItem(item)
        self.count_badge.setText(f"{len(filtered)} disponibles")
        if filtered:
            self.report_list.setCurrentRow(0)
        else:
            self._clear_selection("No hay resultados con esos filtros.")

    def _report_selected(self, current, _previous=None):
        if current:
            report = current.data(Qt.UserRole)
            self._set_selection(Path(report["workbook_path"]), report)

    def _set_selection(self, path, report):
        if self._thread is not None:
            return
        self.generated_path = None
        self.generated_pdf_path = None
        self.excel_path = path
        self.generated_path = None
        self.generated_pdf_path = None
        self.current_program = str(report.get("program") or "")
        self.current_period = str(report.get("period") or "")
        self.selection_badge.setText("LISTO PARA GENERAR")
        self.selection_title.setText(self.current_program or path.stem)
        self.detail_values["program"].setText(self.current_program or "Sin identificar")
        self.detail_values["period"].setText(self.current_period or "Sin identificar")
        self.detail_values["file"].setText(path.name)
        self.detail_values["output"].setText(self._destination().name)
        self.detail_values["events"].setText(self._read_event_total(path))
        self.generate_button.setEnabled(bool(self.current_program and self.current_period))
        self.feedback.setText("Excel listo. Revisa los datos y crea el documento Word.")
        self.open_button.hide()
        self.pdf_button.hide()

    def _read_event_total(self, path):
        try:
            workbook = load_workbook(path, read_only=True, data_only=True)
            try:
                sheet = workbook["Resumen Informe"]
                for row in sheet.iter_rows(min_col=1, max_col=2, values_only=True):
                    if str(row[0] or "").strip().casefold() == "eventos totales":
                        return f"{int(float(row[1] or 0)):,}".replace(",", ".")
            finally:
                workbook.close()
        except Exception:
            return "No disponible"
        return "No disponible"

    def _clear_selection(self, message):
        if self._thread is not None:
            return
        self.generated_path = None
        self.generated_pdf_path = None
        self.open_button.hide()
        self.pdf_button.hide()
        self.excel_path = None
        self.selection_badge.setText("SIN SELECCIÓN")
        self.selection_title.setText("Selecciona un Excel")
        for value in self.detail_values.values():
            value.setText("-")
        self.generate_button.setEnabled(False)
        self.feedback.setText(message)

    def _select_excel(self):
        if self._thread is not None:
            return
        selected, _ = QFileDialog.getOpenFileName(self, "Seleccionar Excel terminado", "", "Archivos Excel (*.xlsx)")
        if not selected:
            return
        path = Path(selected)
        try:
            program, period = self._read_report_identity(path)
        except (OSError, ValueError) as error:
            show_error(self, "No se pudo abrir el informe", str(error))
            return
        if not period or not program:
            show_error(self, "No se pudo identificar el informe", "Selecciona un Excel generado y terminado desde esta aplicacion.")
            return
        self.report_list.clearSelection()
        self._set_selection(path, {"program": program, "period": period, "owner_name": "Archivo externo"})

    @staticmethod
    def _read_report_identity(path):
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            if "Resumen Informe" not in workbook.sheetnames:
                raise ValueError("El Excel no está terminado: falta la hoja Resumen Informe.")
            title = str(workbook["Resumen Informe"]["A1"].value or "")
            match = re.fullmatch(r"Resumen del informe Open LMS - (.+) (\d{4}-[12])", title.strip())
            if not match:
                raise ValueError("No se pudo identificar el programa y el período dentro del Excel.")
            return match.group(1), match.group(2)
        finally:
            workbook.close()

    def _destination(self):
        return build_word_path(self.excel_path.parent, self.current_period, self.current_program)

    def _pdf_destination(self):
        return build_pdf_path(self.excel_path.parent, self.current_period, self.current_program)

    def _generate(self):
        if self._thread is not None:
            return
        if not self.excel_path:
            return
        destination = self._destination()
        if destination.exists() and not ask_confirmation(self, "El informe ya existe", f"Ya existe {destination.name}.\n\nDeseas reemplazarlo?"):
            return
        self._lock_controls()
        self.progress.show()
        self.feedback.setText("Generando graficos, tablas y documento institucional...")
        self._thread = QThread(self)
        excel_path, program, period = self.excel_path, self.current_program, self.current_period
        self._worker = WordGenerationTask(lambda: generate_word_report(excel_path, destination, program, period))
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
        self.feedback.setText(f"Informe creado correctamente: {self.generated_path.name}")
        self.open_button.show()
        self.pdf_button.show()
        show_info(self, "Informe generado", f"El documento se creo correctamente.\n\n{self.generated_path.name}", success=True)

    def _failed(self, message):
        self.feedback.setText("No fue posible crear el documento.")
        show_error(self, "Error al generar el Word", message)

    def _open_generated(self):
        if self.generated_path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.generated_path.resolve())))

    def _generate_pdf(self):
        if self._thread is not None:
            return
        if not self.generated_path or not self.generated_path.is_file():
            show_error(self, "Genera primero el Word", "Primero crea el documento Word para poder generar el PDF.")
            return
        destination = self._pdf_destination()
        if destination.exists() and not ask_confirmation(self, "El PDF ya existe", f"Ya existe {destination.name}.\n\nDeseas reemplazarlo?"):
            return
        self._lock_controls()
        self.progress.show()
        self.feedback.setText("Generando PDF a partir del documento Word...")
        self._thread = QThread(self)
        source = self.generated_path
        self._worker = WordGenerationTask(lambda: convert_word_to_pdf(source, destination))
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._pdf_generated)
        self._worker.failed.connect(self._pdf_failed)
        self._worker.finished.connect(self._thread.quit)
        self._worker.failed.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.failed.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread_finished)
        self._thread.start()

    def _pdf_generated(self, path):
        self.generated_pdf_path = Path(path)
        self.feedback.setText(f"PDF creado correctamente: {self.generated_pdf_path.name}")
        show_info(self, "PDF generado", f"El PDF se guardo correctamente en la carpeta.\n\n{self.generated_pdf_path.name}", success=True)

    def _pdf_failed(self, message):
        self.feedback.setText("No fue posible crear el PDF.")
        show_error(self, "Error al generar el PDF", message)

    @Slot()
    def _thread_finished(self):
        thread = self._thread
        self._worker = None
        self._thread = None
        if thread:
            thread.deleteLater()
        self.progress.hide()
        for control, enabled in getattr(self, "_control_states", {}).items():
            control.setEnabled(enabled)
        self._control_states = {}
        self.generate_button.setEnabled(bool(self.excel_path))
        self.pdf_button.setEnabled(bool(self.generated_path))

    def _lock_controls(self):
        controls = [*self.findChildren(QPushButton), *self.findChildren(QComboBox),
                    *self.findChildren(QListWidget), *self.findChildren(QLineEdit)]
        self._control_states = {control: control.isEnabled() for control in controls}
        for control in controls:
            control.setEnabled(False)
