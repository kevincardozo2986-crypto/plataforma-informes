from pathlib import Path

from PySide6.QtCore import QSize, Qt, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QStackedWidget,
    QWidget,
)

from app.ui.theme import DASHBOARD_STYLESHEET
from app.ui.assistant import anchor_bottom_right
from app.ui.modal_dialogs import MODAL_STYLE, exec_modal
from app.ui.window_chrome import preparar_ventana_sin_marco
from app.ui.excel_process_window import ExcelProcessWindow
from app.ui.word_report_window import WordReportWindow
from app.ui.users_window import UsersPage
from app.services.process_history_service import (
    list_completed_processes,
    list_incomplete_processes,
)

ASSETS = Path(__file__).parent / "assets"


def named(widget, object_name):
    """Asigna nombres QSS sin depender de argumentos no compatibles de PySide6."""
    widget.setObjectName(object_name)
    return widget


class WorkflowPanel(QWidget):
    """Contenedor limpio para los pasos principales del flujo."""


class ProcessCard(QFrame):
    clicked = Signal()

    def __init__(self, number, icon_name, decoration_name, title, description):
        super().__init__()
        self.setObjectName("processCard")
        self.setMinimumHeight(470)
        self.setMaximumHeight(525)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(15, 38, 68, 25))
        self.setGraphicsEffect(shadow)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 22)
        layout.setSpacing(10)
        badge = QLabel(str(number))
        badge.setObjectName("stepBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(34, 34)
        card_title = QLabel(title)
        card_title.setObjectName("processTitle")
        card_title.setAlignment(Qt.AlignCenter)
        body = QLabel(description)
        body.setObjectName("processDescription")
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)

        decoration = QLabel()
        decoration.setObjectName("processDecoration")
        decoration.setAlignment(Qt.AlignCenter)
        decoration.setPixmap(
            QPixmap(str(ASSETS / decoration_name)).scaled(
                330, 230, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        decoration.setMinimumHeight(215)

        button = QPushButton("Abrir módulo    →")
        button.setObjectName("openModuleButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(44)
        button.clicked.connect(self.clicked.emit)
        layout.addWidget(badge, alignment=Qt.AlignLeft)
        layout.addWidget(decoration, 1)
        layout.addWidget(card_title)
        layout.addWidget(body)
        layout.addSpacing(10)
        layout.addWidget(button)


class HistoryRecordWidget(QFrame):
    """Tarjeta compacta para un informe terminado o pendiente."""

    def __init__(self, registro, terminado=False):
        super().__init__()
        self.setObjectName("historyRecordCard")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(13)
        icono = QLabel("✓" if terminado else "↻")
        icono.setObjectName("completedHistoryIcon" if terminado else "pendingHistoryIcon")
        icono.setAlignment(Qt.AlignCenter)
        icono.setFixedSize(38, 38)
        textos = QVBoxLayout()
        textos.setSpacing(3)
        titulo = QLabel(f"{registro['program']}  ·  {registro['period']}")
        titulo.setObjectName("historyRecordTitle")
        detalle = "  ·  ".join(
            valor for valor in (
                registro.get("modality"), registro.get("owner_name", ""),
                registro.get("updated_at"),
            ) if valor
        )
        meta = QLabel(detalle)
        meta.setObjectName("historyRecordMeta")
        textos.addWidget(titulo)
        textos.addWidget(meta)
        estado_texto = "Terminado" if terminado else (
            "Con error" if registro.get("status") == "error"
            else f"Paso {registro.get('completed_step', 0)} de 8"
        )
        estado = QLabel(estado_texto)
        estado.setObjectName(
            "completedHistoryPill" if terminado else
            ("errorHistoryPill" if registro.get("status") == "error" else "pendingHistoryPill")
        )
        estado.setAlignment(Qt.AlignCenter)
        estado.setMinimumWidth(92)
        layout.addWidget(icono)
        layout.addLayout(textos, 1)
        layout.addWidget(estado)


class ModuleDialog(QDialog):
    """Diálogo sencillo para los módulos que todavía no tienen una página propia."""

    def __init__(self, title, description, parent=None):
        super().__init__(parent)
        self.setObjectName("institutionalDialog")
        self.setStyleSheet(MODAL_STYLE)
        self.setWindowTitle(title)
        self.setMinimumSize(480, 260)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(preparar_ventana_sin_marco(self, title, False))
        content = QVBoxLayout()
        content.setContentsMargins(24, 22, 24, 20)
        content.setSpacing(14)

        heading = QLabel(title)
        heading.setStyleSheet("font-size: 18px; font-weight: 700; color: #071D38;")
        body = QLabel(description)
        body.setWordWrap(True)
        body.setStyleSheet("color: #526A82; font-size: 12px;")
        content.addWidget(heading)
        content.addWidget(body)
        content.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        content.addWidget(buttons)
        layout.addLayout(content, 1)


class DashboardWindow(QMainWindow):
    logout_requested = Signal()
    excel_requested = Signal()
    report_requested = Signal()
    history_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Plataforma de Informes")
        self.setMinimumSize(1120, 700)
        self.stack = QStackedWidget()
        self.home_page = self._create_home_page()
        self.stack.addWidget(self.home_page)
        self.excel_page = ExcelProcessWindow(user)
        self.excel_page.back_requested.connect(self._show_dashboard)
        self.stack.addWidget(self.excel_page)
        self.word_page = WordReportWindow(user)
        self.word_page.back_requested.connect(self._show_dashboard)
        self.stack.addWidget(self.word_page)
        self.excel_requested.connect(self._open_excel)
        if user["role"] == "admin":
            self.users_page = UsersPage(user)
            self.users_page.back_requested.connect(self._show_dashboard)
            self.stack.addWidget(self.users_page)
        contenedor = QWidget()
        diseno_ventana = QVBoxLayout(contenedor)
        diseno_ventana.setContentsMargins(0, 0, 0, 0)
        diseno_ventana.setSpacing(0)
        diseno_ventana.addWidget(
            preparar_ventana_sin_marco(
                self, "Plataforma de Informes USTA", controles_completos=True
            )
        )
        diseno_ventana.addWidget(self.stack, 1)
        self.setCentralWidget(contenedor)
        self.setStyleSheet(DASHBOARD_STYLESHEET)
        anchor_bottom_right(self.home_page, "inicio")

    def _create_home_page(self):
        page = named(QWidget(), "dashboardPage")
        root = QHBoxLayout(page)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._create_sidebar())
        root.addWidget(self._create_content(), 1)
        return page

    def _nav(self, text, icon_name="document.svg", active=False):
        button = QPushButton(f"  {text}")
        button.setObjectName("activeNavButton" if active else "navButton")
        button.setIcon(QIcon(str(ASSETS / icon_name)))
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(42)
        return button

    def _create_sidebar(self):
        sidebar = named(QFrame(), "dashboardSidebar")
        sidebar.setFixedWidth(255)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(26, 28, 22, 24)
        layout.setSpacing(7)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(str(ASSETS / "usta-crest.png")).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(62, 62)
        university = named(QLabel("UNIVERSIDAD\nSANTO TOMÁS"), "sidebarUniversity")
        brand.addWidget(logo)
        brand.addWidget(university)
        layout.addLayout(brand)
        layout.addSpacing(26)
        layout.addWidget(named(QLabel("Plataforma\nde Informes"), "sidebarTitle"))
        layout.addWidget(named(QLabel("Transforma datos en\ndecisiones claras."), "sidebarSubtitle"))
        layout.addSpacing(22)
        nav = [
            ("Procesos", "history.svg", self._show_dashboard, True),
            ("Informes", "document.svg", self._open_reports, False),
            ("Historial", "history.svg", self._open_history, False),
            ("Plantillas", "excel.svg", self.excel_requested.emit, False),
            ("Configuración", "edit.svg", self._open_configuration, False),
            ("Ayuda", "users.svg", self._open_help, False),
        ]
        for text, icon, callback, active in nav:
            button = self._nav(text, icon, active)
            if callback:
                button.clicked.connect(callback)
            layout.addWidget(button)
        if self.user["role"] == "admin":
            users = self._nav("Gestionar usuarios", "users.svg")
            users.clicked.connect(self._open_users)
            layout.addWidget(users)
        layout.addStretch()
        logout = self._nav("Cerrar sesión", "logout.svg")
        logout.setObjectName("logoutNavButton")
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)
        return sidebar

    def _create_content(self):
        content = named(QWidget(), "dashboardContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 26, 32, 20)
        layout.setSpacing(11)
        name = self.user.get("full_name") or self.user.get("username", "Usuario")
        header = QHBoxLayout()
        header.addWidget(named(QLabel("⌂    Inicio    /    Procesos"), "dashboardSection"))
        header.addStretch()
        header.addWidget(named(QLabel(f"♢    {name}  ⌄"), "dashboardUser"))
        layout.addLayout(header)
        layout.addSpacing(24)
        layout.addWidget(named(QLabel("¿Qué quieres crear hoy?"), "routeTitle"))
        layout.addWidget(named(QLabel("Sigue estos pasos para convertir tus datos en informes institucionales listos para usar."), "routeSubtitle"))
        layout.addSpacing(22)
        workflow = named(WorkflowPanel(), "workflowPanel")
        cards = QHBoxLayout(workflow)
        cards.setContentsMargins(0, 0, 0, 0)
        cards.setSpacing(20)
        data = [
            (1, "process-excel.png", "card-excel-scene.png", "Preparar Excel", "Organiza y valida la información exportada desde Moodle.", self.excel_requested.emit),
            (2, "process-report.png", "card-report-scene.png", "Crear informe", "Convierte el Excel en el documento institucional.", self._open_report_creation),
            (3, "process-history.png", "card-history-scene.png", "Consultar historial", "Encuentra rápidamente los informes anteriores.", self._open_history),
        ]
        for number, icon, decoration, title, body, callback in data:
            card = ProcessCard(number, icon, decoration, title, body)
            card.clicked.connect(callback)
            cards.addWidget(card)
        workflow.setMinimumHeight(470)
        workflow.setMaximumHeight(525)
        layout.addWidget(workflow, 1)
        layout.addStretch(1)
        layout.addSpacing(6)
        layout.addWidget(named(QLabel("Versión 1.0.0   •   Plataforma de Informes USTA"), "dashboardFooter"))
        return content

    def _open_users(self):
        if hasattr(self, "users_page"):
            self.stack.setCurrentWidget(self.users_page)

    def _open_excel(self):
        self.excel_page.preparar_nuevo_informe()
        self.stack.setCurrentWidget(self.excel_page)

    def _open_reports(self):
        """Muestra todos los informes finalizados disponibles para el usuario."""
        informes = list_completed_processes(self.user)
        dialog = QDialog(self)
        dialog.setObjectName("institutionalDialog")
        dialog.setStyleSheet(MODAL_STYLE)
        dialog.setWindowTitle("Informes terminados")
        dialog.setMinimumSize(720, 460)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(
            preparar_ventana_sin_marco(dialog, "Informes terminados", False)
        )
        content = QVBoxLayout()
        content.setContentsMargins(24, 22, 24, 20)
        content.setSpacing(12)
        title_row = QHBoxLayout()
        title = QLabel("Historial de informes terminados")
        title.setObjectName("historyDialogTitle")
        count = QLabel(f"{len(informes)} informes")
        count.setObjectName("historyCountBadge")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(count)
        description = QLabel(
            "Consulta los informes completados y abre el archivo Excel guardado."
        )
        description.setStyleSheet("color: #526A82; font-size: 11px;")
        results = QListWidget()
        results.setObjectName("reportHistoryList")
        results.setSpacing(8)
        for informe in informes:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, informe)
            item.setSizeHint(QSize(0, 76))
            results.addItem(item)
            results.setItemWidget(item, HistoryRecordWidget(informe, terminado=True))
        if not informes:
            results.addItem("Todavía no hay informes terminados.")

        def abrir_seleccionado():
            item = results.currentItem()
            informe = item.data(Qt.UserRole) if item else None
            if not informe:
                return
            ruta = Path(informe["workbook_path"])
            if not ruta.is_file():
                exec_modal(
                    ModuleDialog(
                        "Archivo no encontrado",
                        "El registro existe, pero el archivo fue movido o eliminado.",
                        dialog,
                    )
                )
                return
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(ruta.resolve())))

        actions = QHBoxLayout()
        close = QPushButton("Cerrar")
        close.setObjectName("dialogSecondaryButton")
        close.clicked.connect(dialog.reject)
        open_button = QPushButton("Abrir informe")
        open_button.setObjectName("dialogPrimaryButton")
        open_button.setEnabled(bool(informes))
        open_button.clicked.connect(abrir_seleccionado)
        results.itemDoubleClicked.connect(lambda _: abrir_seleccionado())
        actions.addStretch()
        actions.addWidget(close)
        actions.addWidget(open_button)
        content.addLayout(title_row)
        content.addWidget(description)
        content.addWidget(results, 1)
        content.addLayout(actions)
        layout.addLayout(content, 1)
        exec_modal(dialog)

    def _open_report_creation(self):
        """Mantiene la acción de creación separada del archivo de terminados."""
        self.word_page.reset()
        self.stack.setCurrentWidget(self.word_page)

    def _open_history(self):
        procesos = list_incomplete_processes(self.user)
        dialog = QDialog(self)
        dialog.setObjectName("institutionalDialog")
        dialog.setStyleSheet(MODAL_STYLE)
        dialog.setWindowTitle("Historial de informes")
        dialog.setMinimumSize(680, 430)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(preparar_ventana_sin_marco(dialog, "Historial de informes", False))
        content = QVBoxLayout()
        content.setContentsMargins(24, 22, 24, 20)
        content.setSpacing(12)
        title_row = QHBoxLayout()
        title = QLabel("Informes pendientes")
        title.setObjectName("historyDialogTitle")
        count = QLabel(f"{len(procesos)} pendientes")
        count.setObjectName("historyCountBadge")
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(count)
        description = QLabel(
            "Selecciona un proceso para continuar desde el último paso completado."
        )
        description.setStyleSheet("color: #526A82; font-size: 11px;")
        results = QListWidget()
        results.setObjectName("reportHistoryList")
        results.setSpacing(8)
        for proceso in procesos:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, proceso)
            item.setSizeHint(QSize(0, 76))
            results.addItem(item)
            results.setItemWidget(item, HistoryRecordWidget(proceso))
        if not procesos:
            results.addItem("No hay informes pendientes. Todos los procesos están completos.")

        actions = QHBoxLayout()
        saved = QPushButton("Buscar Excel guardados")
        saved.setObjectName("dialogSecondaryButton")
        saved.clicked.connect(lambda: (dialog.accept(), self._open_saved_history()))
        resume = QPushButton("Continuar informe")
        resume.setObjectName("dialogPrimaryButton")
        resume.setEnabled(bool(procesos))

        def continue_selected():
            item = results.currentItem()
            proceso = item.data(Qt.UserRole) if item else None
            if proceso and self.excel_page.resume_process(proceso):
                dialog.accept()
                self.stack.setCurrentWidget(self.excel_page)

        resume.clicked.connect(continue_selected)
        results.itemDoubleClicked.connect(lambda _: continue_selected())
        close = QPushButton("Cerrar")
        close.setObjectName("dialogSecondaryButton")
        close.clicked.connect(dialog.reject)
        actions.addWidget(saved)
        actions.addStretch()
        actions.addWidget(close)
        actions.addWidget(resume)
        content.addLayout(title_row)
        content.addWidget(description)
        content.addWidget(results, 1)
        content.addLayout(actions)
        layout.addLayout(content, 1)
        exec_modal(dialog)

    def _open_saved_history(self):
        carpeta = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta donde buscar informes"
        )
        if not carpeta:
            return

        archivos = sorted(Path(carpeta).rglob("*.xlsx"))
        dialog = QDialog(self)
        dialog.setObjectName("institutionalDialog")
        dialog.setStyleSheet(MODAL_STYLE)
        dialog.setWindowTitle("Historial de informes")
        dialog.setMinimumSize(620, 400)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(preparar_ventana_sin_marco(dialog, "Historial de informes", False))
        content = QVBoxLayout()
        content.setContentsMargins(24, 22, 24, 20)
        content.setSpacing(12)
        title = QLabel("Informes encontrados")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #071D38;")
        content.addWidget(title)
        results = QListWidget()
        results.addItems([str(archivo) for archivo in archivos])
        if not archivos:
            results.addItem("No se encontraron archivos Excel en esta carpeta.")
        content.addWidget(results)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        content.addWidget(buttons)
        layout.addLayout(content, 1)
        exec_modal(dialog)

    def _open_configuration(self):
        dialog = QDialog(self)
        dialog.setObjectName("institutionalDialog")
        dialog.setStyleSheet(MODAL_STYLE)
        dialog.setWindowTitle("Configuración")
        dialog.setMinimumSize(520, 280)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(preparar_ventana_sin_marco(dialog, "Configuración", False))
        content = QVBoxLayout()
        content.setContentsMargins(24, 22, 24, 20)
        content.setSpacing(12)
        title = QLabel("Configuración de informes")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #071D38;")
        content.addWidget(title)
        description = QLabel(
            "Define la carpeta base que se usará al preparar informes. "
            "Esta configuración se aplica a la sesión actual."
        )
        description.setWordWrap(True)
        content.addWidget(description)
        folder = QLabel(self.excel_page.base_directory or "No seleccionada")
        folder.setWordWrap(True)
        content.addWidget(folder)
        choose = QPushButton("Seleccionar carpeta base")
        choose.clicked.connect(lambda: self._choose_base_directory(folder))
        content.addWidget(choose)
        content.addStretch()
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(dialog.reject)
        content.addWidget(buttons)
        layout.addLayout(content, 1)
        exec_modal(dialog)

    def _choose_base_directory(self, label):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta base")
        if not carpeta:
            return
        self.excel_page.base_directory = carpeta
        self.excel_page.base_label.setText(carpeta)
        self.excel_page.base_label.setToolTip(carpeta)
        self.excel_page._update_destination()
        label.setText(carpeta)

    def _open_help(self):
        exec_modal(
            ModuleDialog(
                "Ayuda",
                "1. En Informes selecciona el CSV exportado desde Moodle.\n"
                "2. Elige la carpeta base y completa la configuración académica.\n"
                "3. Ejecuta los pasos disponibles para crear el archivo Excel.\n"
                "4. Usa Historial para consultar los archivos .xlsx guardados.",
                self,
            )
        )

    def _show_dashboard(self):
        self.stack.setCurrentWidget(self.home_page)
