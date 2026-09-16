"""Mascota de ayuda contextual: explica qué hace cada lugar de la app."""

from pathlib import Path

from PySide6.QtCore import QEvent, QRect, QRectF, QSize, Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
)

from app.ui.modal_dialogs import MODAL_STYLE, exec_modal

ASSETS = Path(__file__).parent / "assets"
MASCOT_IMAGE = ASSETS / "student-cutout-v2.png"
TOMY_BADGE = ASSETS / "tomy-badge.png"

HELP_CONTENT = {
    "historial": {
        "title": "Tus informes, en un solo lugar",
        "what": "Aquí puedes consultar tus procesos anteriores y encontrar los archivos que ya generaste.",
        "steps": ["Selecciona un proceso para consultar su información.", "Usa la opción de continuar para retomar un proceso pendiente.", "Consulta los archivos guardados para encontrar los informes disponibles."],
        "tip": "Si moviste un archivo de carpeta, puede que debas localizarlo de nuevo.",
    },
    "configuracion": {
        "title": "Organiza dónde guardas tu trabajo",
        "what": "Aquí eliges la carpeta donde la aplicación guardará tus informes.",
        "steps": ["Revisa la carpeta de destino que aparece en pantalla.", "Pulsa el botón para elegir una carpeta y selecciona la ubicación que prefieras."],
        "tip": "Elige una carpeta fácil de encontrar y con permisos de escritura.",
    },
    "inicio": {
        "title": "Aquí empieza todo",
        "what": "Este es el inicio. Desde estas 3 tarjetas eliges qué hacer.",
        "steps": [
            "1. Preparar Excel: organiza el CSV de Moodle.",
            "2. Crear informe: convierte el Excel en Word y PDF.",
            "3. Consultar historial: encuentra informes anteriores.",
        ],
        "tip": "Si es tu primera vez, abre Ayuda en el menú lateral.",
    },
    "excel": {
        "title": "Generación de Excel",
        "what": "Aquí conviertes el CSV de Moodle en el libro Excel institucional.",
        "steps": [
            "1. Elige periodo, nivel, modalidad y programa.",
            "2. Selecciona la carpeta destino y el CSV.",
            "3. Pulsa Cargar CSV y ejecuta los pasos en orden.",
            "4. Previsualiza y guarda el Excel resultante.",
        ],
        "tip": "Si un paso falla, puedes reintentarlo sin cerrar la app.",
    },
    "word": {
        "title": "Informe Word y PDF",
        "what": "Aquí conviertes un Excel terminado en Word institucional y PDF.",
        "steps": [
            "1. Busca el Excel terminado en la lista o selecciónalo.",
            "2. Revisa programa, periodo y eventos registrados.",
            "3. Crea el documento Word con la plantilla.",
            "4. Genera el PDF con LibreOffice desde aquí mismo.",
        ],
        "tip": "Primero crea el Word; el PDF se genera a partir de él.",
    },
    "usuarios": {
        "title": "Gestión de usuarios",
        "what": "Aquí el administrador crea y controla las cuentas.",
        "steps": [
            "1. Crea usuarios con Nuevo usuario.",
            "2. Edita nombre, rol o contraseña desde la tabla.",
            "3. Activa o desactiva cuentas sin eliminarlas.",
        ],
        "tip": "No puedes quitarte tus propios permisos ni eliminarte.",
    },
}


def mascot_pixmap(size=96):
    pixmap = QPixmap(str(MASCOT_IMAGE))
    if pixmap.isNull():
        return QPixmap(size, size)
    return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def draw_dog_face(size=64):
    """Insignia de la app: perrito moderno estilo flat con degradado USTA."""
    badge = QPixmap(str(TOMY_BADGE)) if TOMY_BADGE.is_file() else QPixmap()
    if not badge.isNull():
        from PySide6.QtGui import QPainterPath

        # Render the badge in a circular avatar viewport, excluding its outer canvas.
        avatar = QPixmap(size * 2, size * 2)
        avatar.fill(Qt.transparent)
        painter = QPainter(avatar)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        circle = QPainterPath()
        circle.addEllipse(QRectF(0, 0, size * 2, size * 2))
        painter.setClipPath(circle)
        source = QRectF(badge.width() * .016, badge.height() * .017,
                        badge.width() * .968, badge.height() * .943)
        painter.drawPixmap(QRectF(0, 0, size * 2, size * 2), badge, source)
        painter.end()
        avatar.setDevicePixelRatio(2)
        return avatar
    from PySide6.QtGui import QLinearGradient, QPainterPath

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    sin_borde = QPen(Qt.NoPen)
    lado = float(size)

    def fraccion(x, y, w, h):
        return (lado * x, lado * y, lado * w, lado * h)

    # Fondo insignia con degradado
    degradado = QLinearGradient(0, 0, lado, lado)
    degradado.setColorAt(0.0, QColor("#1B6FD0"))
    degradado.setColorAt(1.0, QColor("#0A2F5C"))
    painter.setPen(sin_borde)
    painter.setBrush(QBrush(degradado))
    painter.drawEllipse(0, 0, lado, lado)
    # Anillo dorado institucional
    painter.setPen(QPen(QColor("#D6A419"), max(2.0, lado * 0.028)))
    painter.setBrush(QBrush(Qt.NoBrush))
    margen = lado * 0.045
    painter.drawEllipse(margen, margen, lado - 2 * margen, lado - 2 * margen)
    painter.setPen(sin_borde)

    # Orejas caídas modernas
    painter.setBrush(QBrush(QColor("#2A4E80")))
    izquierda = QPainterPath()
    izquierda.moveTo(lado * 0.20, lado * 0.22)
    izquierda.cubicTo(lado * 0.06, lado * 0.26, lado * 0.05, lado * 0.48, lado * 0.16, lado * 0.58)
    izquierda.cubicTo(lado * 0.24, lado * 0.64, lado * 0.28, lado * 0.44, lado * 0.28, lado * 0.30)
    izquierda.closeSubpath()
    painter.drawPath(izquierda)
    derecha = QPainterPath()
    derecha.moveTo(lado * 0.80, lado * 0.22)
    derecha.cubicTo(lado * 0.94, lado * 0.26, lado * 0.95, lado * 0.48, lado * 0.84, lado * 0.58)
    derecha.cubicTo(lado * 0.76, lado * 0.64, lado * 0.72, lado * 0.44, lado * 0.72, lado * 0.30)
    derecha.closeSubpath()
    painter.drawPath(derecha)

    # Cabeza
    painter.setBrush(QBrush(QColor("#F8ECD2")))
    painter.drawEllipse(*fraccion(0.17, 0.20, 0.66, 0.62))
    # Mancha moderna sobre un ojo
    painter.setBrush(QBrush(QColor("#E3C893")))
    painter.drawEllipse(*fraccion(0.55, 0.26, 0.24, 0.26))

    # Rubor sutil
    painter.setBrush(QBrush(QColor(232, 130, 110, 70)))
    painter.drawEllipse(*fraccion(0.22, 0.55, 0.12, 0.08))
    painter.drawEllipse(*fraccion(0.66, 0.55, 0.12, 0.08))

    # Ojos grandes con brillo
    painter.setBrush(QBrush(QColor("#10233B")))
    painter.drawEllipse(*fraccion(0.315, 0.44, 0.105, 0.125))
    painter.drawEllipse(*fraccion(0.58, 0.44, 0.105, 0.125))
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawEllipse(*fraccion(0.335, 0.46, 0.04, 0.045))
    painter.drawEllipse(*fraccion(0.60, 0.46, 0.04, 0.045))

    # Hocico
    painter.setBrush(QBrush(QColor("#FFFFFF")))
    painter.drawEllipse(*fraccion(0.32, 0.60, 0.36, 0.20))
    # Nariz redondeada
    painter.setBrush(QBrush(QColor("#10233B")))
    nariz = QPainterPath()
    nariz.moveTo(lado * 0.44, lado * 0.635)
    nariz.cubicTo(lado * 0.44, lado * 0.61, lado * 0.56, lado * 0.61, lado * 0.56, lado * 0.635)
    nariz.cubicTo(lado * 0.56, lado * 0.665, lado * 0.44, lado * 0.665, lado * 0.44, lado * 0.635)
    nariz.closeSubpath()
    painter.drawPath(nariz)
    # Sonrisa
    painter.setPen(QPen(QColor("#10233B"), max(1.5, lado * 0.022), Qt.SolidLine, Qt.RoundCap))
    painter.setBrush(QBrush(Qt.NoBrush))
    sonrisa = QPainterPath()
    sonrisa.moveTo(lado * 0.50, lado * 0.68)
    sonrisa.cubicTo(lado * 0.50, lado * 0.725, lado * 0.44, lado * 0.73, lado * 0.415, lado * 0.705)
    painter.drawPath(sonrisa)
    sonrisa2 = QPainterPath()
    sonrisa2.moveTo(lado * 0.50, lado * 0.68)
    sonrisa2.cubicTo(lado * 0.50, lado * 0.725, lado * 0.56, lado * 0.73, lado * 0.585, lado * 0.705)
    painter.drawPath(sonrisa2)
    # Collar dorado con placa
    painter.setPen(sin_borde)
    painter.setBrush(QBrush(QColor("#D6A419")))
    painter.drawEllipse(*fraccion(0.38, 0.80, 0.24, 0.09))
    painter.setBrush(QBrush(QColor("#FFF3CF")))
    painter.drawEllipse(*fraccion(0.465, 0.815, 0.07, 0.06))
    painter.end()
    return pixmap


SHORT_HELP = {
    "inicio": ("Soy Tomy 🐶", "Elige una tarjeta para empezar."),
    "excel": ("Soy Tomy 🐶", "Carga el CSV y sigue los pasos en orden."),
    "word": ("Soy Tomy 🐶", "Elige el Excel, crea el Word y luego el PDF."),
    "usuarios": ("Soy Tomy 🐶", "Crea y administra las cuentas aquí."),
}


class MascotBuddy(QWidget):
    """Perrito insignia con nubecita siempre visible, anclado abajo a la derecha."""

    def __init__(self, host, context):
        super().__init__(host)
        self.context = context
        self._host = host
        self._welcome_seen = False
        self._welcome = None
        nombre, mensaje = SHORT_HELP.get(context, ("Soy Tomy 🐶", "¿En qué te ayudo?"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        nube = QFrame(objectName="mascotBubble")
        nube.setCursor(Qt.PointingHandCursor)
        nube.setToolTip("Dame click para ver más")
        nube.setStyleSheet(
            "QFrame#mascotBubble { background-color: #FFFFFF; border: 1px solid #D9E4F1;"
            " border-radius: 14px; }"
            "QLabel#mascotBubbleTitle { color: #0B315A; font-family: 'Segoe UI'; font-size: 12px; font-weight: 700; }"
            "QLabel#mascotBubbleText { color: #52657C; font-family: 'Segoe UI'; font-size: 11px; }"
        )
        burbuja = QVBoxLayout(nube)
        burbuja.setContentsMargins(12, 9, 12, 9)
        burbuja.setSpacing(2)
        titulo = QLabel(nombre.replace("🐶", "").strip(), objectName="mascotBubbleTitle")
        texto = QLabel(mensaje, objectName="mascotBubbleText")
        texto.setWordWrap(True)
        burbuja.addWidget(titulo)
        burbuja.addWidget(texto)
        guide = QPushButton("Muéstrame cómo  →")
        guide.setCursor(Qt.PointingHandCursor)
        guide.setStyleSheet("QPushButton { color: #0B5DAC; background: #EFF5FD; border: none; border-radius: 6px; padding: 6px; font-family: 'Segoe UI'; font-size: 11px; font-weight: 600; } QPushButton:hover { background: #DCEBFC; }")
        guide.clicked.connect(lambda: show_assistant(self.window(), context))
        burbuja.addWidget(guide)
        nube.setMaximumWidth(230)
        nube.mousePressEvent = lambda event: show_assistant(self.window(), context)
        self._nube = nube

        self._cara = QLabel()
        self._cara.setPixmap(draw_dog_face(80))
        self._cara.setFixedSize(84, 84)
        self._cara.setAlignment(Qt.AlignCenter)
        self._cara.setCursor(Qt.OpenHandCursor)
        self._cara.setToolTip("Arrástrame, o dame click para mostrar/ocultar la nube")
        self._cara.mousePressEvent = self._empezar_arrastre
        self._cara.mouseMoveEvent = self._arrastrar
        self._cara.mouseReleaseEvent = self._terminar_arrastre
        self._arrastrando = False
        self._movido_por_usuario = False
        self._punto_ancla = None

        layout.addWidget(nube)
        layout.addWidget(self._cara, alignment=Qt.AlignBottom)
        self.adjustSize()

        host.installEventFilter(self)
        self._reposition()
        self.show()

    def eventFilter(self, obj, event):
        if obj is self._host and event.type() in (QEvent.Hide, QEvent.Resize):
            if self._welcome is not None:
                self._welcome.finish()
        if obj is self._host and event.type() in (QEvent.Resize, QEvent.Show):
            if self._movido_por_usuario:
                self._contener()
            else:
                self._reposition()
            self.raise_()
            if event.type() == QEvent.Show and self.context == "inicio" and not self._welcome_seen:
                QTimer.singleShot(0, self._show_welcome)
        return super().eventFilter(obj, event)

    def _show_welcome(self):
        if self._welcome_seen or not self._host.isVisible():
            return
        self._welcome_seen = True
        if not (ASSETS / "tomy-welcome-cutout.png").is_file():
            return
        self._nube.hide()
        self.adjustSize()
        self._reposition()
        self._welcome = TomyWelcome(self)

    def _reposition(self):
        ancho = self.sizeHint().width() or self.width() or 300
        alto = self.sizeHint().height() or self.height() or 80
        x = max(8, self._host.width() - ancho - 16)
        y = max(8, self._host.height() - alto - 16)
        self.move(x, y)
        self.raise_()

    def _contener(self):
        x = min(max(self.x(), 0), max(self._host.width() - self.width(), 0))
        y = min(max(self.y(), 0), max(self._host.height() - self.height(), 0))
        self.move(x, y)
        self.raise_()

    def _empezar_arrastre(self, event):
        if event.button() == Qt.LeftButton:
            self._arrastrando = True
            self._punto_ancla = event.globalPosition().toPoint()
            self._origen = self.pos()
            self._cara.setCursor(Qt.ClosedHandCursor)
            event.accept()

    def _arrastrar(self, event):
        if not self._arrastrando or self._punto_ancla is None:
            return
        if not (event.buttons() & Qt.LeftButton):
            return
        destino = event.globalPosition().toPoint()
        delta = destino - self._punto_ancla
        if delta.manhattanLength() > 4:
            self._movido_por_usuario = True
        self.move(self._origen + delta)
        self._contener()
        event.accept()

    def _terminar_arrastre(self, event):
        fue_clic = (
            self._punto_ancla is not None
            and (event.globalPosition().toPoint() - self._punto_ancla).manhattanLength() <= 4
        )
        self._arrastrando = False
        self._punto_ancla = None
        self._cara.setCursor(Qt.OpenHandCursor)
        if fue_clic:
            self._nube.setVisible(not self._nube.isVisible())
            self.adjustSize()
            self._contener()
        event.accept()


def anchor_bottom_right(host, context):
    """Fija el perrito con su nube abajo a la derecha del módulo."""
    buddy = MascotBuddy(host, context)
    host._mascot_buddy = buddy
    return buddy


class WelcomeSpeech(QWidget):
    """Globo grande y lindo orientado hacia la boca de Tomy."""

    def paintEvent(self, event):
        from PySide6.QtGui import QFont, QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        # Sombras suaves detrás del globo
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(10, 45, 90, 28))
        shadow = QPainterPath()
        shadow.addRoundedRect(QRectF(17, 6, self.width()-19, self.height()-16), 26, 26)
        painter.drawPath(shadow)
        # Globo blanco con borde institucional
        bubble = QPainterPath()
        bubble.addRoundedRect(QRectF(15, 1, self.width()-17, self.height()-19), 24, 24)
        tail = QPainterPath()
        tail.moveTo(30, self.height()-32)
        tail.lineTo(2, self.height()-4)
        tail.lineTo(62, self.height()-20)
        tail.closeSubpath()
        painter.setPen(QPen(QColor("#0B63CE"), 2.0))
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawPath(bubble.united(tail))
        # Título grande
        painter.setPen(QColor("#0B3A6B"))
        title_font = QFont("Segoe UI", 26)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(QRectF(23, 10, self.width()-33, 52), Qt.AlignHCenter | Qt.AlignTop, "¡Bienvenidos!")
        # Subtítulo lindo
        painter.setPen(QColor("#52657C"))
        sub_font = QFont("Segoe UI", 12)
        sub_font.setBold(False)
        painter.setFont(sub_font)
        painter.drawText(
            QRectF(23, 62, self.width()-33, self.height()-90),
            Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
            "Soy Tomy, tu guía en la plataforma",
        )
        painter.end()


class TomyWelcome(QWidget):
    """Bienvenida de una sola aparición; se recoge hacia la mascota real."""

    def __init__(self, buddy):
        super().__init__(buddy._host)
        self.buddy = buddy
        self._finished = False
        self._collapsing = False
        self.setGeometry(self.parentWidget().rect())
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        # Más grande: ocupa buena parte de la pantalla sin salirse.
        height = max(380, min(620, self.height() - 30))
        sprite_width = int(height * 1024 / 1536)
        raw = QPixmap(str(ASSETS / "tomy-welcome-cutout.png"))
        scaled = raw.scaled(
            sprite_width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.sprite = QLabel(self)
        self.sprite.setStyleSheet("background: transparent; border: none;")
        self.sprite.setPixmap(scaled)
        self.sprite.setAlignment(Qt.AlignCenter)
        self.sprite.setScaledContents(False)
        # Sombra elegante bajo Tomy
        try:
            from PySide6.QtWidgets import QGraphicsDropShadowEffect

            glow = QGraphicsDropShadowEffect(self.sprite)
            glow.setBlurRadius(45)
            glow.setOffset(0, 14)
            glow.setColor(QColor(10, 45, 90, 70))
            self.sprite.setGraphicsEffect(glow)
        except Exception:
            pass
        final = QRect(
            (self.width() - sprite_width) // 2 - 90,
            (self.height() - height) // 2 - 10,
            sprite_width,
            height,
        )
        self.speech = WelcomeSpeech(self)
        self.speech.setGeometry(
            final.x() + int(sprite_width * 0.68),
            final.y() + int(height * 0.10),
            350, 135,
        )
        self.sprite.setGeometry(final.translated(0, 26))
        self.animation = QPropertyAnimation(self.sprite, b"geometry", self)
        self.animation.setDuration(700)
        self.animation.setStartValue(self.sprite.geometry())
        self.animation.setEndValue(final)
        self.animation.setEasingCurve(QEasingCurve.OutBack)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.collapse)
        buddy.hide()
        self.show()
        self.raise_()
        self.animation.start()
        self.timer.start(3800)

    def collapse(self):
        if self._collapsing or self._finished:
            return
        self._collapsing = True
        self.timer.stop()
        self.animation.stop()
        effect = QGraphicsOpacityEffect(self.speech)
        self.speech.setGraphicsEffect(effect)
        self.fade = QPropertyAnimation(effect, b"opacity", self)
        self.fade.setDuration(250)
        self.fade.setStartValue(1.0)
        self.fade.setEndValue(0.0)
        self.fade.start()
        destination = self.buddy._cara.mapTo(self.parentWidget(), self.buddy._cara.rect().topLeft())
        self.animation.setDuration(800)
        self.animation.setStartValue(self.sprite.geometry())
        self.animation.setEndValue(QRect(destination, self.buddy._cara.size()))
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.finished.connect(self.finish)
        self.animation.start()

    def finish(self):
        if self._finished:
            return
        self._finished = True
        self.timer.stop()
        self.animation.stop()
        self.buddy._welcome = None
        self.buddy.show()
        self.buddy.raise_()
        self.hide()
        self.deleteLater()


class MascotButton(QPushButton):
    """Botsito de ayuda para anclar en la esquina de cada módulo."""

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setObjectName("mascotButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("¿Qué hago aquí?")
        self.setFixedSize(44, 44)
        self.setIcon(draw_dog_face(40))
        self.setIconSize(QSize(36, 36))
        self.setStyleSheet(
            "QPushButton#mascotButton { background-color: #FFFFFF; border: 2px solid #0B67D1;"
            " border-radius: 22px; font-size: 20px; font-weight: 900; color: #0B67D1; }"
            "QPushButton#mascotButton:hover { background-color: #EAF3FC; }"
        )
        self.setText("?" if self.icon().isNull() else "")
        self.clicked.connect(lambda: show_assistant(self.window(), context))


class MascotDialog(QDialog):
    """Guía contextual de Tomy, presentada un paso a la vez."""

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.content = HELP_CONTENT[context]
        self.step_index = 0
        self.setWindowTitle("Tomy | " + self.content["title"])
        self.setObjectName("tomyGuide")
        self.setModal(True)
        self.setFixedWidth(560)
        self.setStyleSheet("""
            QDialog#tomyGuide { background: #F6F8FC; }
            QDialog#tomyGuide QLabel, QDialog#tomyGuide QPushButton { font-family: 'Segoe UI'; }
            QFrame#guideHero { background: #103D6C; border-radius: 14px; }
            QLabel#guideEyebrow { color: #F4CE67; font-size: 11px; font-weight: 700; }
            QLabel#guideTitle { color: white; font-size: 22px; font-weight: 700; }
            QLabel#guideIntro { color: #42566D; font-size: 14px; }
            QFrame#guideStep { background: white; border: 1px solid #DFE7F1; border-radius: 12px; }
            QLabel#guideCounter { color: #0B63BA; font-size: 11px; font-weight: 700; }
            QLabel#guideInstruction { color: #19334F; font-size: 17px; font-weight: 600; }
            QLabel#guideTip { color: #6C5420; background: #FFF6DD; padding: 14px; border-radius: 10px; font-size: 12px; }
            QPushButton { border: 1px solid #CCD9E8; background: white; color: #24496E; border-radius: 8px; padding: 10px 16px; font-size: 12px; }
            QPushButton:hover { background: #E8F1FC; }
            QPushButton:disabled { color: #98A4B4; background: #F0F3F7; }
            QPushButton#guideNext { background: #0B63CE; color: white; border: none; font-weight: 700; }
            QPushButton#guideNext:hover { background: #094FAD; }
        """)
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)
        hero = QFrame(objectName="guideHero")
        heading = QHBoxLayout(hero)
        heading.setContentsMargins(18, 18, 18, 18)
        avatar = QLabel()
        avatar.setPixmap(draw_dog_face(88))
        heading.addWidget(avatar)
        text = QVBoxLayout()
        text.addWidget(QLabel("SOY TOMY, TU GUÍA", objectName="guideEyebrow"))
        title = QLabel(self.content["title"], objectName="guideTitle")
        title.setWordWrap(True)
        text.addWidget(title)
        heading.addLayout(text, 1)
        root.addWidget(hero)
        intro = QLabel(self.content["what"], objectName="guideIntro")
        intro.setWordWrap(True)
        root.addWidget(intro)
        card = QFrame(objectName="guideStep")
        step_layout = QVBoxLayout(card)
        step_layout.setContentsMargins(20, 18, 20, 18)
        step_layout.setSpacing(12)
        self.counter = QLabel(objectName="guideCounter")
        self.instruction = QLabel(objectName="guideInstruction")
        self.instruction.setWordWrap(True)
        self.instruction.setMinimumHeight(80)
        step_layout.addWidget(self.counter)
        step_layout.addWidget(self.instruction)
        root.addWidget(card)
        tip = QLabel("CONSEJO DE TOMY\n" + self.content["tip"], objectName="guideTip")
        tip.setWordWrap(True)
        root.addWidget(tip)
        actions = QHBoxLayout()
        close = QPushButton("Cerrar guía")
        close.clicked.connect(self.reject)
        self.previous = QPushButton("Anterior")
        self.previous.clicked.connect(self._previous_step)
        self.next_button = QPushButton(objectName="guideNext")
        self.next_button.clicked.connect(self._next_step)
        actions.addWidget(close)
        actions.addStretch()
        actions.addWidget(self.previous)
        actions.addWidget(self.next_button)
        root.addLayout(actions)
        self._update_step()

    def _update_step(self):
        import re
        steps = self.content["steps"]
        self.counter.setText(f"PASO {self.step_index + 1} DE {len(steps)}")
        self.instruction.setText(re.sub(r"^\d+\.\s*", "", steps[self.step_index]))
        self.previous.setEnabled(self.step_index > 0)
        self.next_button.setText("Entendido" if self.step_index == len(steps) - 1 else "Siguiente →")

    def _previous_step(self):
        self.step_index = max(0, self.step_index - 1)
        self._update_step()

    def _next_step(self):
        if self.step_index == len(self.content["steps"]) - 1:
            self.accept()
        else:
            self.step_index += 1
            self._update_step()


def show_assistant(parent, context):
    if context not in HELP_CONTENT:
        return
    exec_modal(MascotDialog(context, parent))
