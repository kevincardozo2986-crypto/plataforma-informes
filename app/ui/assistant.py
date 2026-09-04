"""Mascota de ayuda contextual: explica qué hace cada lugar de la app."""

from pathlib import Path

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.modal_dialogs import MODAL_STYLE, exec_modal

ASSETS = Path(__file__).parent / "assets"
MASCOT_IMAGE = ASSETS / "student-cutout-v2.png"

HELP_CONTENT = {
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
        nombre, mensaje = SHORT_HELP.get(context, ("Soy Tomy 🐶", "¿En qué te ayudo?"))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        nube = QFrame(objectName="mascotBubble")
        nube.setCursor(Qt.PointingHandCursor)
        nube.setToolTip("Dame click para ver más")
        nube.setStyleSheet(
            "QFrame#mascotBubble { background-color: #FFFFFF; border: 2px solid #0B67D1;"
            " border-radius: 12px; }"
            "QLabel#mascotBubbleTitle { color: #0B315A; font-size: 11px; font-weight: 900; }"
            "QLabel#mascotBubbleText { color: #52657C; font-size: 10px; }"
        )
        burbuja = QVBoxLayout(nube)
        burbuja.setContentsMargins(12, 9, 12, 9)
        burbuja.setSpacing(2)
        titulo = QLabel(nombre, objectName="mascotBubbleTitle")
        texto = QLabel(mensaje, objectName="mascotBubbleText")
        texto.setWordWrap(True)
        burbuja.addWidget(titulo)
        burbuja.addWidget(texto)
        nube.setMaximumWidth(230)
        nube.mousePressEvent = lambda event: show_assistant(self.window(), context)
        self._nube = nube

        self._cara = QLabel()
        self._cara.setPixmap(draw_dog_face(56))
        self._cara.setFixedSize(60, 60)
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
        if obj is self._host and event.type() in (QEvent.Resize, QEvent.Show):
            if self._movido_por_usuario:
                self._contener()
            else:
                self._reposition()
            self.raise_()
        return super().eventFilter(obj, event)

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


class MascotButton(QPushButton):
    """Botsito de ayuda para anclar en la esquina de cada módulo."""

    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setObjectName("mascotButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("¿Qué hago aquí?")
        self.setFixedSize(44, 44)
        self.setIcon(mascot_pixmap(40))
        self.setIconSize(QSize(36, 36))
        self.setStyleSheet(
            "QPushButton#mascotButton { background-color: #FFFFFF; border: 2px solid #0B67D1;"
            " border-radius: 22px; font-size: 20px; font-weight: 900; color: #0B67D1; }"
            "QPushButton#mascotButton:hover { background-color: #EAF3FC; }"
        )
        self.setText("?" if self.icon().isNull() else "")
        self.clicked.connect(lambda: show_assistant(self.window(), context))


class MascotDialog(QDialog):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        content = HELP_CONTENT[context]
        self.setObjectName("institutionalDialog")
        self.setWindowTitle(content["title"])
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setStyleSheet(MODAL_STYLE)

        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(0, 0, 0, 0)
        exterior.setSpacing(0)
        cuerpo = QHBoxLayout()
        cuerpo.setContentsMargins(24, 22, 24, 12)
        cuerpo.setSpacing(16)

        imagen = QLabel()
        imagen.setPixmap(mascot_pixmap(110))
        imagen.setFixedSize(116, 116)
        imagen.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        cuerpo.addWidget(imagen)

        burbuja = QVBoxLayout()
        burbuja.setSpacing(8)
        titulo = QLabel(content["title"])
        titulo.setObjectName("dialogTitle")
        que = QLabel(content["what"])
        que.setObjectName("dialogMessage")
        que.setWordWrap(True)
        pasos = QLabel("\n".join(content["steps"]))
        pasos.setObjectName("dialogMessage")
        pasos.setWordWrap(True)
        tip = QLabel(f"Tip: {content['tip']}")
        tip.setObjectName("dialogHint")
        tip.setWordWrap(True)
        burbuja.addWidget(titulo)
        burbuja.addWidget(que)
        burbuja.addWidget(pasos)
        burbuja.addWidget(tip)
        cuerpo.addLayout(burbuja, 1)
        exterior.addLayout(cuerpo)

        pie = QHBoxLayout()
        pie.setContentsMargins(24, 8, 24, 20)
        pie.addStretch()
        cerrar = QPushButton("Entendido")
        cerrar.setObjectName("dialogPrimaryButton")
        cerrar.clicked.connect(self.accept)
        pie.addWidget(cerrar)
        exterior.addLayout(pie)


def show_assistant(parent, context):
    if context not in HELP_CONTENT:
        return
    exec_modal(MascotDialog(context, parent))
