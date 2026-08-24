from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.theme import DASHBOARD_STYLESHEET
from app.ui.excel_process_window import ExcelProcessWindow
from app.ui.users_window import UsersPage

ASSETS = Path(__file__).parent / "assets"


def named(widget, object_name):
    """Asigna nombres QSS sin depender de argumentos no compatibles de PySide6."""
    widget.setObjectName(object_name)
    return widget


class WorkflowPanel(QWidget):
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#8D99AA"), 2, Qt.SolidLine, Qt.RoundCap))
        y = int(self.height() * .43)
        painter.drawLine(int(self.width() * .27), y, int(self.width() * .73), y)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#8D99AA"))
        for x in (.39, .61):
            painter.drawEllipse(int(self.width() * x) - 5, y - 5, 10, 10)


class ProcessCard(QFrame):
    clicked = Signal()

    def __init__(self, number, icon_name, decoration_name, title, description):
        super().__init__()
        self.setObjectName("processCard")
        self.setMinimumHeight(260)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(15, 38, 68, 25))
        self.setGraphicsEffect(shadow)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(9)
        badge = QLabel(str(number))
        badge.setObjectName("stepBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(28, 28)
        icon = QLabel()
        icon.setObjectName("processIcon")
        icon.setAlignment(Qt.AlignCenter)
        icon.setPixmap(QPixmap(str(ASSETS / icon_name)).scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        icon.setFixedHeight(102)
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
                360, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        decoration.setMinimumHeight(155)

        button = QPushButton("Abrir módulo    →")
        button.setObjectName("openModuleButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(36)
        button.clicked.connect(self.clicked.emit)
        layout.addWidget(badge, alignment=Qt.AlignLeft)
        layout.addWidget(icon)
        layout.addWidget(card_title)
        layout.addWidget(body)
        layout.addStretch(1)
        layout.addWidget(decoration)
        layout.addStretch(1)
        layout.addWidget(button)


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
        self.excel_page = ExcelProcessWindow()
        self.excel_page.back_requested.connect(self._show_dashboard)
        self.stack.addWidget(self.excel_page)
        self.excel_requested.connect(self._open_excel)
        if user["role"] == "admin":
            self.users_page = UsersPage(user)
            self.users_page.back_requested.connect(self._show_dashboard)
            self.stack.addWidget(self.users_page)
        self.setCentralWidget(self.stack)
        self.setStyleSheet(DASHBOARD_STYLESHEET)

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
        sidebar.setFixedWidth(238)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(24, 24, 20, 22)
        layout.setSpacing(5)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(str(ASSETS / "usta-crest.png")).scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(62, 62)
        university = named(QLabel("UNIVERSIDAD\nSANTO TOMÁS"), "sidebarUniversity")
        brand.addWidget(logo)
        brand.addWidget(university)
        layout.addLayout(brand)
        layout.addSpacing(22)
        layout.addWidget(named(QLabel("Plataforma\nde Informes"), "sidebarTitle"))
        layout.addWidget(named(QLabel("Transforma datos en\ndecisiones claras."), "sidebarSubtitle"))
        layout.addSpacing(18)
        nav = [
            ("Procesos", "history.svg", self._show_dashboard, True),
            ("Informes", "document.svg", self.report_requested.emit, False),
            ("Historial", "history.svg", self.history_requested.emit, False),
            ("Plantillas", "excel.svg", self.excel_requested.emit, False),
            ("Configuración", "edit.svg", None, False),
            ("Ayuda", "users.svg", None, False),
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
        name = self.user.get("full_name") or self.user.get("username", "Usuario")
        initials = "".join(p[0] for p in name.split()[:2]).upper() or "U"
        profile = QHBoxLayout()
        avatar = named(QLabel(initials), "sidebarAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(38, 38)
        role = "Administrador" if self.user["role"] == "admin" else "Analista de datos"
        profile.addWidget(avatar)
        profile.addWidget(named(QLabel(f"<b>{name}</b><br><span>{role}</span>"), "sidebarProfile"), 1)
        layout.addLayout(profile)
        layout.addSpacing(14)
        logout = self._nav("Cerrar sesión", "logout.svg")
        logout.setObjectName("logoutNavButton")
        logout.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout)
        return sidebar

    def _create_content(self):
        content = named(QWidget(), "dashboardContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(36, 24, 36, 18)
        layout.setSpacing(10)
        name = self.user.get("full_name") or self.user.get("username", "Usuario")
        header = QHBoxLayout()
        header.addWidget(named(QLabel("⌂    Inicio    /    Procesos"), "dashboardSection"))
        header.addStretch()
        header.addWidget(named(QLabel(f"♢    {name}  ⌄"), "dashboardUser"))
        layout.addLayout(header)
        line = named(QFrame(), "headerLine")
        line.setFixedHeight(1)
        layout.addWidget(line)
        layout.addSpacing(16)
        layout.addWidget(named(QLabel("TU RUTA DE TRABAJO"), "routeEyebrow"))
        layout.addWidget(named(QLabel("¿Qué quieres crear hoy?"), "routeTitle"))
        layout.addWidget(named(QLabel("Sigue estos pasos para convertir tus datos en informes institucionales listos para usar."), "routeSubtitle"))
        layout.addSpacing(12)
        workflow = named(WorkflowPanel(), "workflowPanel")
        cards = QHBoxLayout(workflow)
        cards.setContentsMargins(0, 0, 0, 0)
        cards.setSpacing(26)
        data = [
            (1, "process-excel.png", "card-excel-scene.png", "Preparar Excel", "Organiza y valida la información exportada desde Moodle.", self.excel_requested.emit),
            (2, "process-report.png", "card-report-scene.png", "Crear informe", "Convierte el Excel en el documento institucional.", self.report_requested.emit),
            (3, "process-history.png", "card-history-scene.png", "Consultar historial", "Encuentra rápidamente los informes anteriores.", self.history_requested.emit),
        ]
        for number, icon, decoration, title, body, callback in data:
            card = ProcessCard(number, icon, decoration, title, body)
            card.clicked.connect(callback)
            cards.addWidget(card)
        layout.addWidget(workflow, 1)
        layout.addSpacing(8)
        layout.addWidget(named(QLabel("Versión 1.0.0   •   Plataforma de Informes USTA"), "dashboardFooter"))
        return content

    def _open_users(self):
        if hasattr(self, "users_page"):
            self.stack.setCurrentWidget(self.users_page)

    def _open_excel(self):
        self.stack.setCurrentWidget(self.excel_page)

    def _show_dashboard(self):
        self.stack.setCurrentWidget(self.home_page)
