import math
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget

from app.ui.theme import DASHBOARD_STYLESHEET
from app.ui.users_window import UsersPage


class AnimatedDashboardPage(QWidget):
    """Fondo orgánico con un movimiento ambiental muy sutil."""

    def __init__(self):
        super().__init__()
        self.setObjectName("dashboardPage")
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._advance_background)
        self._timer.start(45)

    def _advance_background(self):
        self._phase += 0.018
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        drift = math.sin(self._phase) * 12
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(54, 188, 232, 24))
        painter.drawEllipse(self.width() - 250 + drift, 70, 280, 280)
        painter.setBrush(QColor(255, 94, 112, 22))
        painter.drawEllipse(self.width() - 380 - drift, self.height() - 210, 250, 250)
        painter.setBrush(QColor(255, 210, 28, 28))
        painter.drawEllipse(250 + drift, self.height() - 110, 150, 150)


class AnimatedModuleButton(QPushButton):
    """Botón circular que responde al cursor sin desplazar el contenido."""

    def __init__(self, icon_path, object_name):
        super().__init__()
        self.setObjectName(object_name)
        self.setIcon(QIcon(str(icon_path)))
        self.setIconSize(QSize(38, 38))
        self.setFixedSize(104, 104)
        self.setCursor(Qt.PointingHandCursor)
        self._animation = QPropertyAnimation(self, b"iconSize", self)
        self._animation.setDuration(170)
        self._animation.setEasingCurve(QEasingCurve.OutBack)

    def _animate(self, size):
        self._animation.stop()
        self._animation.setStartValue(self.iconSize())
        self._animation.setEndValue(QSize(size, size))
        self._animation.start()

    def enterEvent(self, event):
        self._animate(48)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate(38)
        super().leaveEvent(event)


class ProcessStep(QWidget):
    clicked = Signal()

    def __init__(self, number, icon_name, title, description, variant):
        super().__init__()
        self.setObjectName("processStep")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 8, 18, 8)
        layout.setSpacing(9)
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        number_label = QLabel(number)
        number_label.setObjectName(f"{variant}StepNumber")
        number_label.setAlignment(Qt.AlignCenter)
        number_label.setFixedSize(34, 26)

        assets = Path(__file__).parent / "assets"
        button = AnimatedModuleButton(assets / icon_name, f"{variant}CircleButton")
        button.clicked.connect(self.clicked.emit)

        title_label = QLabel(title)
        title_label.setObjectName("processTitle")
        title_label.setAlignment(Qt.AlignCenter)
        description_label = QLabel(description)
        description_label.setObjectName("processDescription")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        description_label.setMaximumWidth(250)

        hint = QLabel("Abrir módulo  →")
        hint.setObjectName(f"{variant}ProcessHint")
        hint.setAlignment(Qt.AlignCenter)

        layout.addWidget(number_label, alignment=Qt.AlignCenter)
        layout.addWidget(button, alignment=Qt.AlignCenter)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addWidget(hint)


class WorkflowPanel(QWidget):
    """Ruta de procesos conectada, sin contenedores rectangulares."""

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        y = 102
        path = QPainterPath()
        path.moveTo(width * 0.17, y)
        path.cubicTo(width * 0.30, y - 35, width * 0.36, y + 35, width * 0.50, y)
        path.cubicTo(width * 0.63, y - 35, width * 0.70, y + 35, width * 0.83, y)
        pen = QPen(QColor("#D9DDE8"), 3, Qt.DashLine, Qt.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)


class DashboardWindow(QMainWindow):
    """Punto de entrada animado a los módulos de la plataforma."""

    logout_requested = Signal()
    excel_requested = Signal()
    report_requested = Signal()
    history_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Plataforma de Informes")
        self.setMinimumSize(1050, 680)
        self.stack = QStackedWidget()
        self.home_page = self._create_home_page()
        self.stack.addWidget(self.home_page)
        if user["role"] == "admin":
            self.users_page = UsersPage(user)
            self.users_page.back_requested.connect(self._show_dashboard)
            self.stack.addWidget(self.users_page)
        self.setCentralWidget(self.stack)
        self.setStyleSheet(DASHBOARD_STYLESHEET)

    def _create_home_page(self):
        page = AnimatedDashboardPage()
        root = QHBoxLayout(page)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._create_sidebar())
        root.addWidget(self._create_content(), 1)
        return page

    def _create_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("dashboardSidebar")
        sidebar.setFixedWidth(285)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(28, 30, 28, 28)
        layout.setSpacing(12)
        assets = Path(__file__).parent / "assets"

        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(str(assets / "usta-crest.png")).scaled(62, 62, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(66, 66)
        brand_text = QLabel("UNIVERSIDAD\nSANTO TOMÁS")
        brand_text.setObjectName("sidebarUniversity")
        brand.addWidget(logo)
        brand.addWidget(brand_text)
        brand.addStretch()

        system_name = QLabel("Plataforma\nde Informes")
        system_name.setObjectName("sidebarTitle")
        system_subtitle = QLabel("Transforma datos en\ndecisiones claras.")
        system_subtitle.setObjectName("sidebarSubtitle")

        layout.addLayout(brand)
        layout.addSpacing(28)
        layout.addWidget(system_name)
        layout.addWidget(system_subtitle)
        layout.addStretch()

        if self.user["role"] == "admin":
            users_button = QPushButton("  Gestionar usuarios")
            users_button.setObjectName("sidebarUsersButton")
            users_button.setIcon(QIcon(str(assets / "users.svg")))
            users_button.setCursor(Qt.PointingHandCursor)
            users_button.clicked.connect(self._open_users)
            layout.addWidget(users_button)

        logout_button = QPushButton("  Cerrar sesión")
        logout_button.setObjectName("sidebarLogoutButton")
        logout_button.setIcon(QIcon(str(assets / "logout.svg")))
        logout_button.setCursor(Qt.PointingHandCursor)
        logout_button.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_button)
        return sidebar

    def _create_content(self):
        content = QWidget()
        content.setObjectName("dashboardContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(48, 34, 48, 34)
        layout.setSpacing(16)

        name = self.user.get("full_name") or self.user.get("username", "Usuario")
        top = QHBoxLayout()
        section = QLabel("INICIO  /  PROCESOS")
        section.setObjectName("dashboardSection")
        greeting = QLabel(f"Hola, {name}")
        greeting.setObjectName("dashboardGreetingPill")
        top.addWidget(section)
        top.addStretch()
        top.addWidget(greeting)

        eyebrow = QLabel("TU RUTA DE TRABAJO")
        eyebrow.setObjectName("routeEyebrow")
        title = QLabel("¿Qué quieres crear hoy?")
        title.setObjectName("routeTitle")
        subtitle = QLabel("Avanza por el flujo o entra directamente al proceso que necesitas.")
        subtitle.setObjectName("routeSubtitle")

        workflow = WorkflowPanel()
        workflow.setObjectName("workflowPanel")
        workflow_layout = QHBoxLayout(workflow)
        workflow_layout.setContentsMargins(12, 18, 12, 12)
        workflow_layout.setSpacing(12)
        excel = ProcessStep("01", "excel.svg", "Preparar Excel", "Organiza la información exportada desde Moodle.", "excel")
        report = ProcessStep("02", "document.svg", "Crear informe", "Convierte el Excel en el documento institucional.", "report")
        history = ProcessStep("03", "history.svg", "Consultar historial", "Encuentra rápidamente los informes anteriores.", "history")
        excel.clicked.connect(self.excel_requested.emit)
        report.clicked.connect(self.report_requested.emit)
        history.clicked.connect(self.history_requested.emit)
        workflow_layout.addWidget(excel, 1)
        workflow_layout.addWidget(report, 1)
        workflow_layout.addWidget(history, 1)

        status = QFrame()
        status.setObjectName("flowStatus")
        status_layout = QHBoxLayout(status)
        status_layout.setContentsMargins(20, 11, 20, 11)
        status_dot = QLabel("●")
        status_dot.setObjectName("statusDot")
        status_text = QLabel("Los módulos están preparados para conectar sus procesos próximamente.")
        status_text.setObjectName("statusText")
        status_layout.addWidget(status_dot)
        status_layout.addWidget(status_text)
        status_layout.addStretch()

        layout.addLayout(top)
        layout.addSpacing(18)
        layout.addWidget(eyebrow)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(workflow, 1)
        layout.addWidget(status)
        return content

    def _open_users(self):
        self.stack.setCurrentWidget(self.users_page)

    def _show_dashboard(self):
        self.stack.setCurrentWidget(self.home_page)
