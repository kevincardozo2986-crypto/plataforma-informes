"""Interfaz guiada para transformar un CSV en un libro Excel."""

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Qt, Signal, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QListWidget, QProgressBar, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from app.services.csv_service import estimate_csv_rows, inspect_csv_structure, iter_csv_chunks
from app.services.excel_service import ExcelProcess
from app.services.process_history_service import (
    mark_process_completed,
    save_process_progress,
)
from app.services.report_option_service import (
    add_report_option,
    delete_report_option,
    list_report_options,
    update_report_option,
)
from app.services.report_path_service import (
    copy_source_csv,
    create_report_directory,
    prepare_report_paths,
)
from app.ui.excel_preview_dialog import ExcelPreviewDialog
from app.ui.modal_dialogs import (
    ask_confirmation,
    ask_text,
    exec_modal,
    show_error,
    show_info,
    show_warning,
)
from app.ui.theme import EXCEL_MODULE_STYLESHEET
from app.ui.window_chrome import preparar_ventana_sin_marco


class BackgroundTask(QObject):
    finished = Signal(object)
    failed = Signal(str)
    progress = Signal(int)

    def __init__(self, operacion):
        super().__init__()
        self.operacion = operacion

    @Slot()
    def run(self):
        try:
            resultado = self.operacion(self.progress.emit)
        except Exception as error_operacion:
            self.failed.emit(str(error_operacion))
        else:
            self.finished.emit(resultado)


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
        self.button.setEnabled(state in {"available", "error"})


class OptionManagementDialog(QDialog):
    """Ventana exclusiva para administrar los valores de un selector."""

    def __init__(self, usuario_actual, categoria, nombre_visible, parent=None):
        super().__init__(parent)
        self.usuario_actual = usuario_actual
        self.categoria = categoria
        self.nombre_visible = nombre_visible
        self.setObjectName("optionManagementDialog")
        self.setWindowTitle(f"Administrar {nombre_visible}")
        self.setMinimumSize(440, 390)
        self._crear_interfaz()
        self._recargar_lista()

    def _crear_interfaz(self):
        diseno = QVBoxLayout(self)
        diseno.setContentsMargins(0, 0, 0, 0)
        diseno.setSpacing(0)
        diseno.addWidget(
            preparar_ventana_sin_marco(
                self, f"Administrar {self.nombre_visible}", controles_completos=False
            )
        )
        contenido = QVBoxLayout()
        contenido.setContentsMargins(24, 22, 24, 20)
        contenido.setSpacing(12)

        titulo = QLabel(f"Administrar {self.nombre_visible}")
        titulo.setObjectName("optionDialogTitle")
        ayuda = QLabel(
            "Agrega, edita o elimina las opciones disponibles para los usuarios."
        )
        ayuda.setObjectName("optionDialogHelp")
        ayuda.setWordWrap(True)
        self.lista_opciones = QListWidget()
        self.lista_opciones.setObjectName("optionList")

        acciones = QHBoxLayout()
        boton_agregar = QPushButton("+  Agregar")
        boton_agregar.setObjectName("primaryExcelButton")
        boton_agregar.clicked.connect(self._agregar)
        boton_editar = QPushButton("Editar")
        boton_editar.setObjectName("secondaryExcelButton")
        boton_editar.clicked.connect(self._editar)
        boton_eliminar = QPushButton("Eliminar")
        boton_eliminar.setObjectName("dangerOptionButton")
        boton_eliminar.clicked.connect(self._eliminar)
        acciones.addWidget(boton_agregar)
        acciones.addWidget(boton_editar)
        acciones.addWidget(boton_eliminar)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.setObjectName("secondaryExcelButton")
        boton_cerrar.clicked.connect(self.accept)
        pie = QHBoxLayout()
        pie.addStretch()
        pie.addWidget(boton_cerrar)

        contenido.addWidget(titulo)
        contenido.addWidget(ayuda)
        contenido.addWidget(self.lista_opciones, 1)
        contenido.addLayout(acciones)
        contenido.addLayout(pie)
        diseno.addLayout(contenido, 1)

    def _recargar_lista(self, seleccionar=None):
        self.lista_opciones.clear()
        self.lista_opciones.addItems(list_report_options(self.categoria))
        if seleccionar:
            coincidencias = self.lista_opciones.findItems(
                seleccionar, Qt.MatchFixedString
            )
            if coincidencias:
                self.lista_opciones.setCurrentItem(coincidencias[0])
        elif self.lista_opciones.count():
            self.lista_opciones.setCurrentRow(0)

    def _texto_solicitud(self):
        if self.categoria == "period":
            return "Periodo con formato AAAA-S (ejemplo: 2026-1):"
        return f"Nombre de {self.nombre_visible}:"

    def _agregar(self):
        valor, confirmado = ask_text(
            self, "Agregar opción", self._texto_solicitud()
        )
        if confirmado:
            try:
                guardado = add_report_option(
                    self.usuario_actual, self.categoria, valor
                )
                self._recargar_lista(guardado)
            except (PermissionError, ValueError) as error:
                show_warning(self, "No se pudo agregar", str(error))

    def _editar(self):
        elemento = self.lista_opciones.currentItem()
        if not elemento:
            return
        valor_actual = elemento.text()
        valor_nuevo, confirmado = ask_text(
            self, "Editar opción", self._texto_solicitud(), valor_actual
        )
        if confirmado:
            try:
                guardado = update_report_option(
                    self.usuario_actual, self.categoria, valor_actual, valor_nuevo
                )
                self._recargar_lista(guardado)
            except (PermissionError, ValueError) as error:
                show_warning(self, "No se pudo editar", str(error))

    def _eliminar(self):
        elemento = self.lista_opciones.currentItem()
        if not elemento:
            return
        valor = elemento.text()
        confirmado = ask_confirmation(
            self,
            "Eliminar opción",
            f'¿Deseas eliminar "{valor}"?',
        )
        if not confirmado:
            return
        try:
            delete_report_option(self.usuario_actual, self.categoria, valor)
            self._recargar_lista()
        except (PermissionError, ValueError) as error:
            show_warning(self, "No se pudo eliminar", str(error))


class ExcelProcessWindow(QWidget):
    back_requested = Signal()

    def __init__(self, usuario_actual):
        super().__init__()
        self.usuario_actual = usuario_actual
        self.setObjectName("excelProcessPage")
        self.excel_process = ExcelProcess()
        self.csv_path = None
        self.base_directory = None
        self.report_paths = None
        self.completed_step = 0
        self.steps = []
        self._thread = None
        self._worker = None
        self._control_states = {}
        self.setStyleSheet(EXCEL_MODULE_STYLESHEET)
        self._build_ui()

    def _build_ui(self):
        diseno_exterior = QVBoxLayout(self)
        diseno_exterior.setContentsMargins(0, 0, 0, 0)

        desplazamiento_principal = QScrollArea()
        desplazamiento_principal.setObjectName("excelMainScroll")
        desplazamiento_principal.setWidgetResizable(True)
        desplazamiento_principal.setFrameShape(QFrame.NoFrame)
        desplazamiento_principal.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        contenido = QWidget()
        contenido.setObjectName("excelScrollableContent")
        root = QVBoxLayout(contenido)
        root.setContentsMargins(34, 24, 34, 24)
        root.setSpacing(13)
        desplazamiento_principal.setWidget(contenido)
        diseno_exterior.addWidget(desplazamiento_principal)
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

        configuracion = QFrame()
        configuracion.setObjectName("excelSetupCard")
        grid = QGridLayout(configuracion)
        grid.setContentsMargins(4, 4, 4, 8)
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(7)
        self.period = self._crear_lista_opciones("period")
        self.period.setCurrentText("2026-1")
        self.level = self._crear_lista_opciones("level")
        self.modality = self._crear_lista_opciones("modality")
        self.program = self._crear_lista_opciones("program")

        campos = (
            ("01", "Periodo académico", self.period, "period"),
            ("02", "Nivel académico", self.level, "level"),
            ("03", "Modalidad", self.modality, "modality"),
            ("04", "Programa", self.program, "program"),
        )
        for columna, (numero, nombre, selector, categoria) in enumerate(campos):
            etiqueta = QLabel(f"{numero}   {nombre.upper()}")
            etiqueta.setObjectName("sequenceFieldLabel")
            grid.addWidget(etiqueta, 0, columna)
            grid.addLayout(
                self._crear_fila_selector(selector, categoria, nombre.lower()),
                1,
                columna,
            )
            grid.setColumnStretch(columna, 1)

        self.configuration_summary = QLabel()
        self.configuration_summary.setObjectName("configurationSummary")
        grid.addWidget(self.configuration_summary, 2, 0, 1, 4)
        root.addWidget(configuracion)

        archivos = QFrame()
        archivos.setObjectName("sourceFilesPanel")
        archivos_grid = QGridLayout(archivos)
        archivos_grid.setContentsMargins(16, 12, 16, 13)
        archivos_grid.setHorizontalSpacing(14)
        archivos_grid.setVerticalSpacing(7)

        titulo_archivos = QLabel("ARCHIVOS DE ORIGEN")
        titulo_archivos.setObjectName("sourceFilesTitle")
        archivos_grid.addWidget(titulo_archivos, 0, 0, 1, 3)

        self.file_label = QLabel("Ningún archivo seleccionado")
        self.file_label.setObjectName("selectedCsvLabel")
        select = QPushButton("Examinar")
        select.setObjectName("secondaryExcelButton")
        select.clicked.connect(self._select_csv)
        self.base_label = QLabel("Ninguna carpeta base seleccionada")
        self.base_label.setObjectName("selectedCsvLabel")
        select_base = QPushButton("Seleccionar carpeta")
        select_base.setObjectName("secondaryExcelButton")
        select_base.clicked.connect(self._select_base_directory)
        self.load_button = QPushButton("↑  CARGAR CSV")
        self.load_button.setObjectName("primaryExcelButton")
        self.load_button.setFixedWidth(190)
        self.load_button.setEnabled(False)
        self.load_button.clicked.connect(self._load_csv)

        base_field_label = QLabel("Carpeta base")
        base_field_label.setObjectName("excelFieldLabel")
        file_field_label = QLabel("Archivo CSV")
        file_field_label.setObjectName("excelFieldLabel")

        base_row = QHBoxLayout()
        base_row.addWidget(self.base_label, 1)
        base_row.addWidget(select_base)
        file_row = QHBoxLayout()
        file_row.addWidget(self.file_label, 1)
        file_row.addWidget(select)

        archivos_grid.addWidget(base_field_label, 1, 0)
        archivos_grid.addWidget(file_field_label, 1, 1)
        archivos_grid.addLayout(base_row, 2, 0)
        archivos_grid.addLayout(file_row, 2, 1)
        archivos_grid.addWidget(self.load_button, 2, 2, alignment=Qt.AlignBottom)
        archivos_grid.setColumnStretch(0, 1)
        archivos_grid.setColumnStretch(1, 1)

        destination_title = QLabel("Ruta generada")
        destination_title.setObjectName("destinationTitle")
        self.destination_label = QLabel("Selecciona una carpeta base para construir la ruta institucional.")
        self.destination_label.setObjectName("destinationPath")
        self.destination_label.setWordWrap(True)
        archivos_grid.addWidget(destination_title, 3, 0, 1, 3)
        archivos_grid.addWidget(self.destination_label, 4, 0, 1, 3)
        root.addWidget(archivos)

        for combo in (self.period, self.level, self.modality, self.program):
            combo.currentTextChanged.connect(self._update_destination)
            combo.currentTextChanged.connect(self._actualizar_resumen_configuracion)

        self._actualizar_resumen_configuracion()

        root.addWidget(self._section_header(2, "Flujo de procesamiento"))

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
        scroll.setFixedHeight(245)
        steps_page = QWidget()
        steps_layout = QVBoxLayout(steps_page)
        steps_layout.setContentsMargins(0, 0, 8, 0)
        definitions = (
            ("Crear hoja Original", "Copia todos los datos del CSV sin transformarlos.", True),
            ("Convertir FechaUnix", "Agrega Fecha, Mes y Dia junto a FechaUnix en Original.", True),
            (
                "Procesar docentes",
                "Calcula días distintos, totales y promedios por mes.",
                True,
            ),
        )
        for number, (name, description, executable) in enumerate(definitions, 1):
            step = ProcessStepRow(number, name, description, executable)
            self.steps.append(step)
            steps_layout.addWidget(step)
        self.steps[0].requested.connect(self._create_original)
        self.steps[1].requested.connect(self._prepare_information)
        self.steps[2].requested.connect(self._crear_tabla_docentes)
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

    def _crear_lista_opciones(self, categoria):
        """Crea una lista cerrada con las opciones guardadas en la base de datos."""
        lista = QComboBox()
        lista.setEditable(False)
        lista.addItems(list_report_options(categoria))
        return lista

    def _crear_fila_selector(self, lista, categoria, nombre_visible):
        """Añade un acceso discreto a la administración de la lista."""
        fila = QHBoxLayout()
        fila.setContentsMargins(0, 0, 0, 0)
        fila.setSpacing(6)
        fila.addWidget(lista, 1)

        if self.usuario_actual.get("role") == "admin":
            boton_agregar = QPushButton("+")
            boton_agregar.setObjectName("addOptionButton")
            boton_agregar.setToolTip(f"Administrar {nombre_visible}")
            boton_agregar.setCursor(Qt.PointingHandCursor)
            boton_agregar.setAccessibleName(f"Administrar {nombre_visible}")
            boton_agregar.setFixedSize(30, 30)
            boton_agregar.clicked.connect(
                lambda: self._abrir_administracion(
                    lista, categoria, nombre_visible
                )
            )
            fila.addWidget(boton_agregar)
        return fila

    def _abrir_administracion(self, lista, categoria, nombre_visible):
        """Abre el CRUD en una ventana aparte y refresca el selector al cerrar."""
        valor_anterior = lista.currentText()
        ventana = OptionManagementDialog(
            self.usuario_actual, categoria, nombre_visible, self
        )
        exec_modal(ventana)
        valor_dialogo = (
            ventana.lista_opciones.currentItem().text()
            if ventana.lista_opciones.currentItem()
            else valor_anterior
        )
        lista.clear()
        lista.addItems(list_report_options(categoria))
        lista.setCurrentText(valor_dialogo)
        self._update_destination()

    def _actualizar_resumen_configuracion(self):
        """Explica visualmente cómo se combinarán los cuatro selectores."""
        resumen = "  /  ".join(
            selector.currentText()
            for selector in (self.period, self.level, self.modality, self.program)
        )
        self.configuration_summary.setText(resumen)

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
        ruta_archivo, filtro_seleccionado = QFileDialog.getOpenFileName(
            self, "Seleccionar CSV de Moodle", "", "Archivos CSV (*.csv)"
        )
        if not ruta_archivo:
            return

        ruta_csv = Path(ruta_archivo)
        self.csv_path = ruta_csv
        self.file_label.setText(ruta_csv.name)
        self.file_label.setToolTip(str(ruta_csv))
        self._actualizar_estado_boton_carga(False)
        self._update_destination()

    def _select_base_directory(self):
        ruta_carpeta = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta base de informes"
        )
        if not ruta_carpeta:
            return

        self.base_directory = ruta_carpeta
        self.base_label.setText(ruta_carpeta)
        self.base_label.setToolTip(ruta_carpeta)
        self._update_destination()

    def _update_destination(self):
        self.report_paths = None
        if not self.base_directory:
            self.destination_label.setText("Selecciona una carpeta base para construir la ruta institucional.")
            self.load_button.setEnabled(False)
            return
        try:
            nombre_archivo_origen = self.csv_path or "Informe_Moodle.csv"
            self.report_paths = prepare_report_paths(
                self.base_directory,
                self.period.currentText(),
                self.level.currentText(),
                self.modality.currentText(),
                self.program.currentText(),
                nombre_archivo_origen,
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
        reemplazar_csv = False
        if self.report_paths.source_csv.exists():
            confirmado = ask_confirmation(
                self,
                "El CSV ya existe",
                f"Ya existe {self.report_paths.source_csv.name} en la carpeta del informe.\n\n¿Deseas reemplazar la copia existente?",
            )
            if not confirmado:
                return
            reemplazar_csv = True
        rutas_informe = self.report_paths
        ruta_csv_origen = self.csv_path
        ruta_borrador = (
            rutas_informe.directory
            / f"{rutas_informe.excel.stem}_EN_PROCESO.xlsx"
        )
        self.excel_process = ExcelProcess(ruta_borrador)
        self.completed_step = 0
        datos_academicos = (
            self.base_directory,
            self.period.currentText(),
            self.level.currentText(),
            self.modality.currentText(),
            self.program.currentText(),
        )
        self.steps[0].set_state("pending")
        self._start_background(
            lambda progreso: self._validate_and_copy_csv(
                ruta_csv_origen, rutas_informe, reemplazar_csv, datos_academicos, progreso
            ),
            self._csv_loaded,
            lambda message: self._task_failed(0, "Error al cargar el CSV", message),
        )

    def _validate_and_copy_csv(
        self, ruta_csv_origen, rutas_informe, reemplazar_csv, datos_academicos, informar_progreso
    ):
        informar_progreso(10)
        columnas = inspect_csv_structure(ruta_csv_origen)
        informar_progreso(30)
        create_report_directory(*datos_academicos)
        informar_progreso(45)
        copy_source_csv(
            ruta_csv_origen,
            rutas_informe.source_csv,
            overwrite=reemplazar_csv,
            progress_callback=informar_progreso,
        )
        return len(columnas), rutas_informe

    def _csv_loaded(self, resultado_carga):
        cantidad_columnas, self.report_paths = resultado_carga
        self._actualizar_estado_boton_carga(True)
        self.steps[0].set_state("available")
        self.steps[1].set_state("pending")
        self.steps[2].set_state("pending")
        self.preview_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.feedback.setText(
            f"CSV cargado y validado: {cantidad_columnas} columnas. Ejecuta el paso 1 para crear Original."
        )
        self._guardar_avance(0)

    def _actualizar_estado_boton_carga(self, cargado):
        """Diferencia visualmente un CSV pendiente de uno ya cargado."""
        self.load_button.setText("✓  CSV CARGADO" if cargado else "↑  CARGAR CSV")
        self.load_button.setObjectName(
            "loadedCsvButton" if cargado else "primaryExcelButton"
        )
        self.load_button.style().unpolish(self.load_button)
        self.load_button.style().polish(self.load_button)

    def _task_failed(self, step_index, title, message):
        self.steps[step_index].set_state("error", "Error · Intentar de nuevo")
        self._guardar_avance(self.completed_step, status="error", error_message=message)
        show_error(self, title, message)

    def _start_background(self, operation, on_success, on_error):
        if self._thread and self._thread.isRunning():
            return
        self._bloquear_controles()
        self.feedback.setText("Procesando el archivo por bloques. La aplicación seguirá respondiendo…")
        self.progress_bar.setValue(1)
        self.progress_bar.show()
        self._thread = QThread(self)
        self._worker = BackgroundTask(operation)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.finished.connect(self._finish_background)
        self._worker.failed.connect(self._finish_background)
        self._worker.finished.connect(on_success)
        self._worker.failed.connect(on_error)
        self._thread.start()

    def _bloquear_controles(self):
        """Evita acciones simultáneas mientras se modifica el Excel."""
        controles = [
            *self.findChildren(QPushButton),
            *self.findChildren(QComboBox),
        ]
        self._control_states = {
            control: control.isEnabled() for control in controles
        }
        for control in controles:
            control.setEnabled(False)

    def _restaurar_controles(self):
        """Recupera el estado que cada control tenía antes del proceso."""
        for control, estaba_habilitado in self._control_states.items():
            try:
                control.setEnabled(estaba_habilitado)
            except RuntimeError:
                pass
        self._control_states.clear()

    @Slot()
    def _finish_background(self, *_):
        self.progress_bar.hide()
        self._thread.quit()
        self._thread.wait()
        self._worker.deleteLater()
        self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self._restaurar_controles()
        self.load_button.setEnabled(bool(self.csv_path and self.base_directory))
        excel_disponible = self.excel_process.exists
        self.preview_button.setEnabled(excel_disponible)
        self.save_button.setEnabled(excel_disponible)

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
        total_filas = estimate_csv_rows(self.csv_path)
        return self.excel_process.create_original_from_chunks(
            iter_csv_chunks(self.csv_path, prepare=prepare),
            total_rows=total_filas,
            progress_callback=progress,
        )

    def _original_created(self, resultado_creacion):
        cantidad_filas, cantidad_columnas = resultado_creacion
        self.steps[0].set_state("completed")
        self.steps[1].set_state("available")
        self.steps[2].set_state("pending")
        self.preview_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.feedback.setText(
            f"Hoja Original creada: {cantidad_filas:,} registros y {cantidad_columnas} columnas."
        )
        self.completed_step = 1
        self._guardar_avance(1)

    def _information_prepared(self, resultado_preparacion):
        cantidad_filas, cantidad_columnas = resultado_preparacion
        self.steps[1].set_state("completed")
        self.steps[2].set_state("available")
        self.preview_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.feedback.setText(
            f"FechaUnix convertida: se actualizaron {cantidad_filas:,} registros en la hoja Original."
        )
        self.completed_step = 2
        self._guardar_avance(2)

    def _crear_tabla_docentes(self):
        self.steps[2].set_state("available", "Procesando…")
        self._start_background(
            lambda progreso: self.excel_process.crear_tabla_docentes(progreso),
            self._tabla_docentes_creada,
            lambda mensaje: self._task_failed(
                2, "Error al crear Tabla Dinamica Docentes", mensaje
            ),
        )

    def _tabla_docentes_creada(self, resultado):
        cantidad_filas, meses = resultado
        self.steps[2].set_state("completed")
        self.preview_button.setEnabled(True)
        self.save_button.setEnabled(True)
        self.feedback.setText(
            f"Tabla Dinamica Docentes creada: {cantidad_filas:,} filas; "
            f"meses: {', '.join(meses)}."
        )
        self.completed_step = 3
        self._guardar_avance(3)

    def _guardar_avance(self, paso_completado, status="in_progress", error_message=None):
        """Guarda el punto de recuperación sin interrumpir el proceso si SQLite falla."""
        if not self.report_paths or not self.excel_process.path:
            return
        try:
            save_process_progress(
                self.usuario_actual,
                self.period.currentText(),
                self.level.currentText(),
                self.modality.currentText(),
                self.program.currentText(),
                self.base_directory,
                self.report_paths.source_csv,
                self.excel_process.path,
                paso_completado,
                status,
                error_message,
            )
        except Exception as error:
            self.feedback.setText(
                f"El proceso continúa, pero no se pudo guardar el punto de recuperación: {error}"
            )

    def resume_process(self, proceso):
        """Restaura la configuración y habilita el siguiente paso pendiente."""
        ruta_excel = Path(proceso["workbook_path"])
        ruta_csv = Path(proceso["source_csv"])
        if proceso["completed_step"] > 0 and not ruta_excel.is_file():
            show_error(
                self,
                "No se puede continuar",
                "El Excel de trabajo ya no existe en la ubicación registrada.",
            )
            return False

        selectores = (
            (self.period, proceso["period"]),
            (self.level, proceso["level"]),
            (self.modality, proceso["modality"]),
            (self.program, proceso["program"]),
        )
        for selector, valor in selectores:
            if selector.findText(valor) < 0:
                selector.addItem(valor)
            selector.setCurrentText(valor)

        self.base_directory = proceso["base_directory"]
        self.csv_path = ruta_csv
        self.base_label.setText(str(self.base_directory))
        self.base_label.setToolTip(str(self.base_directory))
        self.file_label.setText(ruta_csv.name)
        self.file_label.setToolTip(str(ruta_csv))
        self._update_destination()
        self.excel_process = ExcelProcess(ruta_excel)
        self.completed_step = int(proceso["completed_step"])

        for indice, paso in enumerate(self.steps):
            if indice < self.completed_step:
                paso.set_state("completed")
            elif indice == self.completed_step:
                paso.set_state("available", "Continuar desde aquí")
            else:
                paso.set_state("pending")
        archivo_disponible = ruta_excel.is_file()
        self.preview_button.setEnabled(archivo_disponible)
        self.save_button.setEnabled(archivo_disponible)
        self.feedback.setText(
            f"Proceso recuperado: {proceso['program']} · paso "
            f"{self.completed_step} de {len(self.steps)} completado."
        )
        return True

    def _preview(self):
        exec_modal(ExcelPreviewDialog(self.excel_process, self))

    def _save(self):
        if not self.report_paths:
            return
        destination = self.report_paths.excel
        if destination.exists():
            confirmado = ask_confirmation(
                self,
                "El Excel ya existe",
                f"Ya existe {destination.name}.\n\n¿Deseas reemplazarlo?",
            )
            if not confirmado:
                return
        try:
            self.excel_process.save_as(destination)
        except OSError as error:
            show_error(self, "No se pudo guardar", str(error))
            return
        self.feedback.setText(f"Excel guardado en {destination}")
        mark_process_completed(self.excel_process.path)
        show_info(
            self,
            "Excel guardado",
            "El archivo se guardó correctamente.",
            success=True,
        )
