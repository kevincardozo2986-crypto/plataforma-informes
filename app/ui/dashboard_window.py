from pathlib import Path
from shutil import copyfile

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
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QStackedWidget,
    QWidget,
)

from app.ui.theme import DASHBOARD_STYLESHEET
from app.ui.assistant import anchor_bottom_right, MascotButton, show_assistant
from app.ui.modal_dialogs import MODAL_STYLE, exec_modal, show_error, show_info
from app.ui.window_chrome import preparar_ventana_sin_marco
from app.ui.excel_process_window import ExcelProcessWindow
from app.ui.word_report_window import WordReportWindow
from app.ui.users_window import UsersPage
from app.ui.history_page import HistoryPage
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
        self.setMinimumHeight(400)
        self.setMaximumHeight(540)
        self.setMinimumWidth(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
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
        card_title.setWordWrap(True)
        body = QLabel(description)
        body.setObjectName("processDescription")
        body.setAlignment(Qt.AlignCenter)
        body.setWordWrap(True)
        body.setMinimumHeight(48)

        decoration = QLabel()
        decoration.setObjectName("processDecoration")
        decoration.setAlignment(Qt.AlignCenter)
        decoration.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Expanding)
        decoration.setPixmap(
            QPixmap(str(ASSETS / decoration_name)).scaled(
                400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        decoration.setMinimumHeight(170)
        self.decoration = decoration
        self._scene = QPixmap(str(ASSETS / decoration_name))

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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.decoration.setPixmap(self._scene.scaled(max(1, self.width()-44), max(170, self.height()-220), Qt.KeepAspectRatio, Qt.SmoothTransformation))


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
        self.history_page = HistoryPage(user)
        self.history_page.back_requested.connect(self._show_dashboard)
        self.history_page.resume_requested.connect(self._resume_history_process)
        self.history_page.browse_requested.connect(self._open_saved_history)
        self.stack.addWidget(self.history_page)
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
                self, "Plataforma de Informes USTA", controles_completos=True,
                mostrar_logo=True,
            )
        )
        diseno_ventana.addWidget(self.stack, 1)
        self.setCentralWidget(contenedor)
        self.setStyleSheet(DASHBOARD_STYLESHEET)
        anchor_bottom_right(self.home_page, "inicio")

    def _create_home_page(self):
        page = named(QWidget(), "dashboardPage")
        page.setStyleSheet('''
            QLabel#processTitle { font-family: "Segoe UI"; font-size: 20px; font-weight: 700; }
            QLabel#processDescription { font-family: "Segoe UI"; font-size: 13px; color: #64799B; }
            QPushButton#openModuleButton { font-size: 14px; font-weight: 600; }
            QFrame#processCard { background: #FFFFFF; border: 1px solid #D6E4F7; border-radius: 20px; }
        ''')
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
        sidebar.setFixedWidth(220)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 22, 20, 22)
        layout.setSpacing(7)
        crest = QLabel()
        crest.setPixmap(QPixmap(str(ASSETS / 'usta-crest.png')).scaled(66, 66, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        crest.setAlignment(Qt.AlignCenter)
        layout.addWidget(crest)
        sidebar_title = named(QLabel("UNIVERSIDAD\nSANTO TOMÁS"), "sidebarTitle")
        sidebar_title.setWordWrap(True)
        sidebar_title.setAlignment(Qt.AlignCenter)
        sidebar_title.setStyleSheet('font-family: Georgia; font-size: 19px; color: white;')
        layout.addWidget(sidebar_title)
        sidebar_subtitle = named(QLabel("Vigilada Mineducación"), "sidebarSubtitle")
        sidebar_subtitle.setAlignment(Qt.AlignCenter)
        sidebar_subtitle.setWordWrap(True)
        layout.addWidget(sidebar_subtitle)
        layout.addSpacing(22)
        nav = [
            ("Procesos", "history.svg", self._show_dashboard, True),
            ("Informes", "document.svg", self._open_reports, False),
            ("Historial", "history.svg", self._open_history, False),
            ("Plantillas", "excel.svg", self.excel_requested.emit, False),
            ("Configuración", "edit.svg", self._open_configuration, False),
            ("Ayuda", "users.svg", self._open_help, False),
            ("Manual de usuario", "document.svg", self._download_user_manual, False),
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
        motto = QLabel('Aquí se construye\ntu propósito.')
        motto.setWordWrap(True)
        motto.setStyleSheet('color: #DCEBFF; font-size: 20px; font-style: italic; padding: 10px 0px;')
        layout.addWidget(motto)
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
        name = (self.user.get("full_name") or self.user.get("username", "Usuario")).strip()
        role = "Administrador" if self.user.get("role") == "admin" else "Usuario"
        initial = name[:1].upper() if name else "U"
        header = QHBoxLayout()
        header.setSpacing(0)
        header.setContentsMargins(0, 0, 0, 0)
        breadcrumb = QHBoxLayout()
        breadcrumb.setSpacing(8)
        breadcrumb.setContentsMargins(0, 0, 0, 0)
        home_icon = named(QLabel("⌂"), "breadcrumbHome")
        home_icon.setAlignment(Qt.AlignVCenter)
        link_inicio = named(QLabel("Inicio"), "breadcrumbLink")
        sep = named(QLabel("/"), "breadcrumbSeparator")
        active = named(QLabel("Procesos"), "breadcrumbActive")
        for w in (home_icon, link_inicio, sep, active):
            breadcrumb.addWidget(w, alignment=Qt.AlignVCenter)
        breadcrumb.addStretch()
        breadcrumb_widget = QWidget()
        breadcrumb_widget.setObjectName("breadcrumbWidget")
        breadcrumb_widget.setLayout(breadcrumb)
        brand_heading = QVBoxLayout()
        brand_title = QLabel('Plataforma de Informes USTA')
        brand_title.setStyleSheet('font-size: 21px; font-weight: 700; color: #082551;')
        brand_heading.addWidget(brand_title)
        brand_heading.addWidget(named(QLabel('Transforma datos en decisiones claras.'), 'routeSubtitle'))
        header.addLayout(brand_heading)
        header.addStretch(1)
        # Pill de usuario: avatar + nombre + rol, alineado verticalmente.
        user_pill = named(QFrame(), "userPill")
        user_pill_layout = QHBoxLayout(user_pill)
        user_pill_layout.setContentsMargins(8, 5, 12, 5)
        user_pill_layout.setSpacing(9)
        avatar = named(QLabel(initial), "userAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(30, 30)
        user_pill_layout.addWidget(avatar)
        user_texts = QVBoxLayout()
        user_texts.setContentsMargins(0, 0, 0, 0)
        user_texts.setSpacing(0)
        user_label = named(QLabel(name), "dashboardUserName")
        user_label.setToolTip(f"{name} · {role}")
        role_label = named(QLabel(role), "roleBadge")
        user_texts.addWidget(user_label)
        user_texts.addWidget(role_label)
        user_pill_layout.addLayout(user_texts)
        header.addWidget(user_pill, alignment=Qt.AlignVCenter)
        layout.addLayout(header)
        divider = named(QFrame(), "headerLine")
        divider.setFixedHeight(1)
        divider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addWidget(divider)
        layout.addWidget(breadcrumb_widget)
        layout.addSpacing(10)
        route_title = named(QLabel('¿Qué quieres <span style="color:#0965EE">crear hoy?</span>'), "routeTitle")
        route_title.setWordWrap(True)
        layout.addWidget(route_title)
        route_subtitle = named(
            QLabel("Sigue estos pasos para convertir tus datos en informes institucionales listos para usar."),
            "routeSubtitle",
        )
        route_subtitle.setWordWrap(True)
        layout.addWidget(route_subtitle)
        layout.addSpacing(18)
        # Scroll responsive: en ventanas angostas las 3 tarjetas hacen scroll
        # horizontal en vez de recortarse (era el corte de tu captura).
        scroll = QScrollArea()
        scroll.setObjectName("workflowScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        workflow = named(WorkflowPanel(), "workflowPanel")
        cards = QHBoxLayout(workflow)
        cards.setContentsMargins(2, 6, 2, 10)
        cards.setSpacing(20)
        data = [
            (1, "process-excel.png", "home-excel.png", "Preparar Excel", "Organiza y valida la información exportada desde Moodle.", self.excel_requested.emit),
            (2, "process-report.png", "home-word.png", "Crear informe", "Convierte el Excel en el documento institucional.", self._open_report_creation),
            (3, "process-history.png", "home-history.png", "Consultar historial", "Encuentra rápidamente los informes anteriores.", self._open_history),
        ]
        for number, icon, decoration, title, body, callback in data:
            card = ProcessCard(number, icon, decoration, title, body)
            card.clicked.connect(callback)
            cards.addWidget(card, 1)
        workflow.setMinimumHeight(420)
        scroll.setWidget(workflow)
        scroll.setMinimumHeight(440)
        layout.addWidget(scroll, 1)
        layout.addSpacing(6)
        footer = named(QLabel("Plataforma de Informes USTA   •   Versión 1.0"), "dashboardFooter")
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)
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
        title_row.addWidget(MascotButton("historial", dialog))
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
        self.history_page.refresh()
        self.stack.setCurrentWidget(self.history_page)

    def _resume_history_process(self, process):
        if self.excel_page.resume_process(process):
            self.stack.setCurrentWidget(self.excel_page)

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
        title_row = QHBoxLayout()
        title_row.addWidget(title, 1)
        title_row.addWidget(MascotButton("historial", dialog))
        content.addLayout(title_row)
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
        title_row = QHBoxLayout()
        title_row.addWidget(title, 1)
        title_row.addWidget(MascotButton("configuracion", dialog))
        content.addLayout(title_row)
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
        show_assistant(self, "inicio")

    def _download_user_manual(self):
        source = ASSETS / 'manual-usuario.pdf'
        if not source.is_file():
            show_error(self, 'Manual no disponible', 'No se encontró el manual en la instalación. Contacta al responsable de la plataforma.')
            return
        selected, _ = QFileDialog.getSaveFileName(
            self, 'Guardar manual de usuario', 'Manual_de_usuario_USTA.pdf', 'Documento PDF (*.pdf)'
        )
        if not selected:
            return
        target = Path(selected)
        if target.suffix.lower() != '.pdf':
            target = target.with_suffix('.pdf')
        try:
            if source.resolve() != target.resolve():
                copyfile(source, target)
        except OSError as error:
            show_error(self, 'No se pudo guardar el manual', str(error))
            return
        show_info(self, 'Manual guardado', f'El manual está listo para consultar, compartir o imprimir.\n\n{target}', success=True)

    def _show_dashboard(self):
        self.stack.setCurrentWidget(self.home_page)
