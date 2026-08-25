from pathlib import Path

from PySide6.QtCore import QRectF, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from app.services.auth_service import authenticate_user
from app.ui.theme import LOGIN_STYLESHEET
from app.ui.window_chrome import preparar_ventana_sin_marco


def create_eye_icon(password_is_visible):
    image = QPixmap(24, 24)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor("#6F7790"), 1.8)
    painter.setPen(pen)
    painter.drawEllipse(QRectF(4, 7, 16, 10))
    painter.drawEllipse(QRectF(10, 10, 4, 4))
    if not password_is_visible:
        painter.drawLine(5, 5, 19, 19)
    painter.end()
    return QIcon(image)


class HeroPanel(QFrame):
    """Panel institucional con las formas orgánicas del diseño aprobado."""

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width, height = self.width(), self.height()

        coral = QPainterPath()
        coral.moveTo(width * 0.58, 0)
        coral.cubicTo(width * 0.55, 70, width * 0.82, 28, width * 0.72, 115)
        coral.cubicTo(width * 0.86, 78, width * 0.90, 155, width, 128)
        coral.lineTo(width, 0)
        coral.closeSubpath()
        painter.fillPath(coral, QColor("#0A4D91"))

        cyan = QPainterPath()
        cyan.moveTo(width * 0.42, height)
        cyan.cubicTo(width * 0.35, height * 0.72, width * 0.65, height * 0.43, width * 0.78, height * 0.34)
        cyan.cubicTo(width * 0.92, height * 0.25, width * 0.86, height * 0.58, width, height * 0.48)
        cyan.lineTo(width, height)
        cyan.closeSubpath()
        painter.fillPath(cyan, QColor("#4A8CC8"))

        yellow = QPainterPath()
        yellow.moveTo(0, height * 0.88)
        yellow.cubicTo(width * 0.14, height * 0.75, width * 0.17, height, width * 0.34, height * 0.91)
        yellow.cubicTo(width * 0.60, height * 0.80, width * 0.74, height * 0.95, width, height * 0.82)
        yellow.lineTo(width, height)
        yellow.lineTo(0, height)
        yellow.closeSubpath()
        painter.fillPath(yellow, QColor("#DCEAF7"))


class LoginWindow(QWidget):
    authentication_succeeded = Signal(dict)

    def __init__(self):
        super().__init__()
        self.password_is_visible = False
        self.setWindowTitle("Inicio de sesión")
        self.setMinimumSize(1000, 680)
        self.setObjectName("loginWindow")
        self._build_ui()
        self.setStyleSheet(LOGIN_STYLESHEET)
        self._connect_events()

    def _build_ui(self):
        diseno_exterior = QVBoxLayout(self)
        diseno_exterior.setContentsMargins(0, 0, 0, 0)
        diseno_exterior.setSpacing(0)
        diseno_exterior.addWidget(
            preparar_ventana_sin_marco(
                self, "Plataforma de Informes USTA", controles_completos=True
            )
        )
        contenido = QWidget()
        contenido.setObjectName("loginContent")
        page_layout = QVBoxLayout(contenido)
        page_layout.setContentsMargins(48, 36, 48, 36)
        page_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setMinimumSize(980, 640)
        card.setMaximumSize(1280, 790)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(48)
        shadow.setOffset(0, 14)
        shadow.setColor(QColor(30, 35, 70, 38))
        card.setGraphicsEffect(shadow)

        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        card_layout.addWidget(self._create_hero_panel(), 54)
        card_layout.addWidget(self._create_form_panel(), 46)
        page_layout.addWidget(card)
        diseno_exterior.addWidget(contenido, 1)

    def _create_hero_panel(self):
        panel = HeroPanel()
        panel.setObjectName("heroPanel")
        layout = QGridLayout(panel)
        layout.setContentsMargins(52, 42, 28, 20)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(0)
        assets = Path(__file__).parent / "assets"

        logo = QLabel()
        logo.setObjectName("universityLogo")
        logo.setAlignment(Qt.AlignCenter)
        logo.setPixmap(QPixmap(str(assets / "usta-crest.png")).scaled(62, 62, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setFixedSize(66, 66)
        brand_name = QLabel("UNIVERSIDAD SANTO TOMÁS\nSECCIONAL TUNJA")
        brand_name.setObjectName("brandName")
        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        brand_row.addWidget(logo)
        brand_row.addWidget(brand_name)
        brand_row.addStretch()

        report_title = QLabel("Informes de")
        report_title.setObjectName("reportTitle")
        report_title.setContentsMargins(34, 24, 0, 0)
        platform_title = QLabel("Uso de Plataforma")
        platform_title.setObjectName("platformTitle")
        platform_title.setContentsMargins(34, 0, 0, 0)
        tagline = QLabel("Consulta y transforma los datos\nen decisiones claras.")
        tagline.setObjectName("tagline")
        tagline.setContentsMargins(34, 0, 0, 0)

        benefits = QVBoxLayout()
        benefits.setSpacing(14)
        benefits.setContentsMargins(64, 42, 0, 0)
        benefits.addWidget(self._create_benefit("01", "Consulta", "información centralizada"))
        benefits.addWidget(self._create_benefit("02", "Analiza", "la actividad de la plataforma"))
        benefits.addWidget(self._create_benefit("03", "Decide", "con datos claros y seguros"))

        student = QLabel()
        student.setObjectName("studentImage")
        student.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        student_image = QPixmap(str(assets / "student-cutout-v2.png"))
        upper_body = student_image.copy(int(student_image.width() * 0.16), 0, int(student_image.width() * 0.68), int(student_image.height() * 0.48))
        student.setPixmap(upper_body.scaled(470, 570, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        layout.addLayout(brand_row, 0, 0, 1, 3)
        layout.addWidget(report_title, 1, 0, 1, 2)
        layout.addWidget(platform_title, 2, 0, 1, 3)
        layout.addWidget(tagline, 3, 0, 1, 2)
        layout.addLayout(benefits, 4, 0, Qt.AlignTop)
        layout.addWidget(student, 3, 1, 3, 2, Qt.AlignBottom | Qt.AlignRight)
        layout.setRowStretch(4, 1)
        layout.setColumnStretch(0, 4)
        layout.setColumnStretch(1, 5)
        return panel

    def _create_benefit(self, number, title, description):
        container = QFrame()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        badge = QLabel(number)
        badge.setObjectName("benefitBadge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setFixedSize(52, 52)
        text = QLabel(f"<b>{title}</b><br><span>{description}</span>")
        text.setObjectName("benefitText")
        layout.addWidget(badge)
        layout.addWidget(text)
        layout.addStretch()
        return container

    def _create_form_panel(self):
        panel = QFrame()
        panel.setObjectName("formPanel")
        panel.setMinimumWidth(470)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(64, 54, 64, 48)
        title = QLabel("Bienvenido")
        title.setObjectName("formTitle")
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Ingresa tus credenciales\npara continuar")
        subtitle.setObjectName("formSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)

        user_label = QLabel("Usuario")
        user_label.setObjectName("fieldLabel")
        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText("Escribe tu usuario")
        self.usuario_input.setClearButtonEnabled(True)
        self.usuario_input.setMinimumHeight(54)
        password_label = QLabel("Contraseña")
        password_label.setObjectName("fieldLabel")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Escribe tu contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(54)
        self.eye_action = self.password_input.addAction(create_eye_icon(False), QLineEdit.TrailingPosition)
        self.eye_action.setToolTip("Mostrar contraseña")
        self.error_label = QLabel()
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        self.login_button = QPushButton("Iniciar sesión      →")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setMinimumHeight(56)
        security = QLabel("Acceso seguro  •  Tus datos están protegidos")
        security.setObjectName("securityText")
        security.setAlignment(Qt.AlignCenter)

        layout.addStretch()
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(subtitle)
        layout.addSpacing(38)
        layout.addWidget(user_label)
        layout.addSpacing(8)
        layout.addWidget(self.usuario_input)
        layout.addSpacing(20)
        layout.addWidget(password_label)
        layout.addSpacing(8)
        layout.addWidget(self.password_input)
        layout.addSpacing(14)
        layout.addWidget(self.error_label)
        layout.addSpacing(14)
        layout.addWidget(self.login_button)
        layout.addStretch()
        layout.addWidget(security)
        return panel

    def _connect_events(self):
        self.login_button.clicked.connect(self._handle_login)
        self.usuario_input.returnPressed.connect(self.password_input.setFocus)
        self.password_input.returnPressed.connect(self._handle_login)
        self.usuario_input.textChanged.connect(self._clear_error)
        self.password_input.textChanged.connect(self._clear_error)
        self.eye_action.triggered.connect(self._toggle_password)

    def _toggle_password(self):
        self.password_is_visible = not self.password_is_visible
        self.password_input.setEchoMode(QLineEdit.Normal if self.password_is_visible else QLineEdit.Password)
        self.eye_action.setIcon(create_eye_icon(self.password_is_visible))
        self.eye_action.setToolTip("Ocultar contraseña" if self.password_is_visible else "Mostrar contraseña")

    def _clear_error(self):
        self.error_label.hide()

    def _show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def _handle_login(self):
        username = self.usuario_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self._show_error("Completa el usuario y la contraseña para continuar.")
            return
        user = authenticate_user(username, password)
        if user is None:
            self.password_input.clear()
            self.password_input.setFocus()
            self._show_error("Las credenciales no son correctas o el usuario está inactivo.")
            return
        self.password_input.clear()
        self.authentication_succeeded.emit(user)
