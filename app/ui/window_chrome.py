"""Barra de título integrada para ventanas y diálogos sin marco nativo."""

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget


CHROME_STYLE = """
QWidget#mainTitleBar {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #05294F, stop:0.55 #073B6E, stop:1 #0A4A84);
    border: none; border-bottom: 2px solid #2C6DA5;
}
QWidget#dialogTitleBar {
    background-color: #0B3F70; border: none; border-bottom: 2px solid #2875B5;
}
QLabel#mainWindowTitle {
    color: #FFFFFF; font-family: "Segoe UI"; font-size: 11px; font-weight: 800;
}
QLabel#mainWindowContext {
    color: #AFC8E2; font-family: "Segoe UI"; font-size: 9px; font-weight: 600;
}
QLabel#dialogWindowTitle {
    color: #FFFFFF; font-family: "Segoe UI"; font-size: 11px; font-weight: 750;
}
QLabel#windowBrandMark { background: transparent; }
QPushButton#mainWindowControl, QPushButton#mainWindowClose,
QPushButton#dialogWindowClose {
    border-radius: 0; padding: 0;
    font-family: "Segoe UI"; font-size: 13px; font-weight: 600;
}
QPushButton#mainWindowControl, QPushButton#mainWindowClose {
    background-color: #124D7F; color: #FFFFFF;
    border: none; border-left: 1px solid #2A628F;
}
QPushButton#mainWindowControl:hover { background-color: #24699F; color: #FFFFFF; }
QPushButton#mainWindowClose:hover { background-color: #C42B3A; color: #FFFFFF; }
QPushButton#dialogWindowClose {
    background-color: #164F80; color: #FFFFFF; font-size: 15px;
    border: none; border-left: 1px solid #2A6698;
}
QPushButton#dialogWindowClose:hover { background-color: #FCE8EA; color: #B42332; }
"""


class WindowTitleBar(QWidget):
    def __init__(self, ventana, titulo, controles_completos=True):
        super().__init__(ventana)
        self.ventana = ventana
        self.controles_completos = controles_completos
        self._posicion_arrastre = None
        self.setObjectName("mainTitleBar" if controles_completos else "dialogTitleBar")
        self.setAttribute(Qt.WA_StyledBackground, True)
        altura = 44 if controles_completos else 40
        self.setFixedHeight(altura)
        self.setStyleSheet(CHROME_STYLE)

        diseno = QHBoxLayout(self)
        diseno.setContentsMargins(14 if controles_completos else 16, 0, 0, 0)
        diseno.setSpacing(0)

        if controles_completos:
            marca = QLabel()
            marca.setObjectName("windowBrandMark")
            ruta_escudo = Path(__file__).parent / "assets" / "usta-crest.png"
            marca.setPixmap(
                QPixmap(str(ruta_escudo)).scaled(
                    25, 25, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            marca.setFixedSize(32, 32)
            marca.setAlignment(Qt.AlignCenter)
            diseno.addWidget(marca)
            diseno.addSpacing(9)
            textos = QHBoxLayout()
            textos.setSpacing(10)
            self.titulo = QLabel(titulo)
            self.titulo.setObjectName("mainWindowTitle")
            contexto = QLabel("•  UNIVERSIDAD SANTO TOMÁS")
            contexto.setObjectName("mainWindowContext")
            textos.addWidget(self.titulo)
            textos.addWidget(contexto)
            diseno.addLayout(textos)
        else:
            marca = QLabel()
            marca.setObjectName("windowBrandMark")
            ruta_escudo = Path(__file__).parent / "assets" / "usta-crest.png"
            marca.setPixmap(
                QPixmap(str(ruta_escudo)).scaled(
                    23, 23, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            marca.setFixedSize(28, 28)
            marca.setAlignment(Qt.AlignCenter)
            diseno.addWidget(marca)
            diseno.addSpacing(8)
            self.titulo = QLabel(titulo)
            self.titulo.setObjectName("dialogWindowTitle")
            diseno.addWidget(self.titulo)
        diseno.addStretch()

        if controles_completos:
            minimizar = self._crear_boton("−", "Minimizar", altura=altura)
            minimizar.clicked.connect(ventana.showMinimized)
            diseno.addWidget(minimizar)

            self.maximizar = self._crear_boton("□", "Maximizar", altura=altura)
            self.maximizar.clicked.connect(self._alternar_maximizado)
            diseno.addWidget(self.maximizar)

        cerrar = self._crear_boton("×", "Cerrar", cerrar=True, altura=altura)
        cerrar.clicked.connect(ventana.close)
        diseno.addWidget(cerrar)

    def _crear_boton(self, texto, ayuda, cerrar=False, altura=40):
        boton = QPushButton(texto)
        if self.controles_completos:
            boton.setObjectName("mainWindowClose" if cerrar else "mainWindowControl")
        else:
            boton.setObjectName("dialogWindowClose")
        boton.setToolTip(ayuda)
        boton.setCursor(Qt.PointingHandCursor)
        boton.setFixedSize(48 if self.controles_completos else 42, altura)
        return boton

    def _alternar_maximizado(self):
        if self.ventana.isMaximized():
            self.ventana.showNormal()
            self.maximizar.setText("□")
            self.maximizar.setToolTip("Maximizar")
        else:
            self.ventana.showMaximized()
            self.maximizar.setText("❐")
            self.maximizar.setToolTip("Restaurar")

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            self._posicion_arrastre = (
                evento.globalPosition().toPoint() - self.ventana.frameGeometry().topLeft()
            )
            evento.accept()

    def mouseMoveEvent(self, evento):
        if self._posicion_arrastre is not None and evento.buttons() & Qt.LeftButton:
            if self.ventana.isMaximized():
                self.ventana.showNormal()
            self.ventana.move(evento.globalPosition().toPoint() - self._posicion_arrastre)
            evento.accept()

    def mouseReleaseEvent(self, evento):
        self._posicion_arrastre = None
        super().mouseReleaseEvent(evento)

    def mouseDoubleClickEvent(self, evento):
        if hasattr(self, "maximizar") and evento.button() == Qt.LeftButton:
            self._alternar_maximizado()
            evento.accept()


def preparar_ventana_sin_marco(ventana, titulo, controles_completos=False):
    ventana.setWindowFlags(ventana.windowFlags() | Qt.FramelessWindowHint)
    return WindowTitleBar(ventana, titulo, controles_completos)
