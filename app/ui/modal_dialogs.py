"""Diálogos modales consistentes con la identidad visual de la aplicación."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)
from app.ui.window_chrome import preparar_ventana_sin_marco


MODAL_STYLE = """
QDialog#institutionalDialog {
    background-color: #FFFFFF; border: 2px solid #0B3F70;
    font-family: "Segoe UI";
}
QFrame#dialogAccentInfo { background-color: #0A4D91; }
QFrame#dialogAccentSuccess { background-color: #16824B; }
QFrame#dialogAccentWarning { background-color: #D58A16; }
QFrame#dialogAccentError { background-color: #B42332; }
QLabel#dialogIconInfo, QLabel#dialogIconSuccess, QLabel#dialogIconWarning, QLabel#dialogIconError {
    color: #FFFFFF; border-radius: 18px; font-size: 18px; font-weight: 900;
}
QLabel#dialogIconInfo { background-color: #0A4D91; }
QLabel#dialogIconSuccess { background-color: #16824B; }
QLabel#dialogIconWarning { background-color: #D58A16; }
QLabel#dialogIconError { background-color: #B42332; }
QLabel#dialogTitle { color: #071D38; font-size: 17px; font-weight: 800; }
QLabel#dialogMessage { color: #52657C; font-size: 11px; }
QLabel#dialogHint { color: #718096; font-size: 10px; }
QLineEdit#dialogInput {
    background-color: #FFFFFF; color: #16314F; border: 1px solid #CBD5E1;
    border-radius: 4px; padding: 10px 11px; font-size: 11px;
}
QLineEdit#dialogInput:focus { border: 2px solid #1B63AF; padding: 9px 10px; }
QPushButton#dialogPrimaryButton, QPushButton#dialogSecondaryButton,
QPushButton#dialogDangerButton {
    min-width: 96px; border-radius: 4px; padding: 9px 16px;
    font-size: 11px; font-weight: 800;
}
QPushButton#dialogPrimaryButton { background-color: #0A4D91; color: #FFFFFF; border: none; }
QPushButton#dialogPrimaryButton:hover { background-color: #073A6F; }
QPushButton#dialogSecondaryButton { background-color: #FFFFFF; color: #31516F; border: 1px solid #CBD5E1; }
QPushButton#dialogSecondaryButton:hover { background-color: #EEF3F8; }
QPushButton#dialogDangerButton { background-color: #B42332; color: #FFFFFF; border: none; }
QPushButton#dialogDangerButton:hover { background-color: #8F1C28; }
QDialog#institutionalDialog QListWidget {
    background-color: #FFFFFF; color: #183455; border: 1px solid #CBD5E1;
    border-radius: 4px; padding: 4px; font-size: 11px;
}
QDialog#institutionalDialog QListWidget::item { padding: 8px; }
QDialog#institutionalDialog QListWidget::item:selected { background-color: #E7F1FA; color: #0A4D91; }
QLabel#historyDialogTitle { color: #071D38; font-size: 20px; font-weight: 800; }
QLabel#historyCountBadge {
    background-color: #E7F1FA; color: #0A4D91; border-radius: 11px;
    padding: 5px 11px; font-size: 10px; font-weight: 800;
}
QListWidget#reportHistoryList {
    background-color: #F6F8FB; border: 1px solid #E1E7EF;
    border-radius: 12px; padding: 10px;
}
QListWidget#reportHistoryList::item { padding: 0px; border: none; border-radius: 10px; }
QListWidget#reportHistoryList::item:selected { background-color: #DDEBFA; }
QFrame#historyRecordCard { background-color: #FFFFFF; border: 1px solid #DFE6EF; border-radius: 10px; }
QLabel#historyRecordTitle { color: #102D50; font-size: 13px; font-weight: 800; }
QLabel#historyRecordMeta { color: #718096; font-size: 10px; }
QLabel#completedHistoryIcon, QLabel#pendingHistoryIcon {
    color: #FFFFFF; border-radius: 19px; font-size: 16px; font-weight: 900;
}
QLabel#completedHistoryIcon { background-color: #16824B; }
QLabel#pendingHistoryIcon { background-color: #1B63AF; }
QLabel#completedHistoryPill, QLabel#pendingHistoryPill, QLabel#errorHistoryPill {
    border-radius: 11px; padding: 5px 9px; font-size: 9px; font-weight: 800;
}
QLabel#completedHistoryPill { background-color: #E3F4EA; color: #137346; }
QLabel#pendingHistoryPill { background-color: #E7F1FA; color: #0A4D91; }
QLabel#errorHistoryPill { background-color: #FCE8EA; color: #B42332; }
QDialog#institutionalDialog QDialogButtonBox QPushButton,
QDialog#institutionalDialog > QPushButton {
    background-color: #FFFFFF; color: #31516F; border: 1px solid #CBD5E1;
    border-radius: 4px; padding: 9px 16px; min-width: 96px;
    font-size: 11px; font-weight: 800;
}
QDialog#institutionalDialog QDialogButtonBox QPushButton:hover,
QDialog#institutionalDialog > QPushButton:hover { background-color: #EEF3F8; }
"""


class MessageDialog(QDialog):
    ICONOS = {"info": "i", "success": "✓", "warning": "!", "error": "×"}

    def __init__(self, titulo, mensaje, tipo="info", confirmar=False, parent=None):
        super().__init__(parent)
        self.setObjectName("institutionalDialog")
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumWidth(440)
        self.setStyleSheet(MODAL_STYLE)

        diseno_exterior = QVBoxLayout(self)
        diseno_exterior.setContentsMargins(0, 0, 0, 0)
        diseno_exterior.setSpacing(0)
        diseno_exterior.addWidget(
            preparar_ventana_sin_marco(self, titulo, controles_completos=False)
        )
        acento = QFrame()
        acento.setObjectName(f"dialogAccent{tipo.title()}")
        acento.setFixedHeight(5)
        diseno_exterior.addWidget(acento)

        contenido = QVBoxLayout()
        contenido.setContentsMargins(24, 22, 24, 20)
        contenido.setSpacing(18)
        cabecera = QHBoxLayout()
        cabecera.setSpacing(14)
        icono = QLabel(self.ICONOS[tipo])
        icono.setObjectName(f"dialogIcon{tipo.title()}")
        icono.setAlignment(Qt.AlignCenter)
        icono.setFixedSize(36, 36)
        textos = QVBoxLayout()
        textos.setSpacing(5)
        etiqueta_titulo = QLabel(titulo)
        etiqueta_titulo.setObjectName("dialogTitle")
        etiqueta_mensaje = QLabel(mensaje)
        etiqueta_mensaje.setObjectName("dialogMessage")
        etiqueta_mensaje.setWordWrap(True)
        textos.addWidget(etiqueta_titulo)
        textos.addWidget(etiqueta_mensaje)
        cabecera.addWidget(icono, alignment=Qt.AlignTop)
        cabecera.addLayout(textos, 1)
        contenido.addLayout(cabecera)

        acciones = QHBoxLayout()
        acciones.addStretch()
        if confirmar:
            cancelar = QPushButton("Cancelar")
            cancelar.setObjectName("dialogSecondaryButton")
            cancelar.clicked.connect(self.reject)
            aceptar = QPushButton("Confirmar")
            aceptar.setObjectName(
                "dialogDangerButton" if tipo == "warning" else "dialogPrimaryButton"
            )
            aceptar.clicked.connect(self.accept)
            acciones.addWidget(cancelar)
            acciones.addWidget(aceptar)
        else:
            aceptar = QPushButton("Entendido")
            aceptar.setObjectName("dialogPrimaryButton")
            aceptar.clicked.connect(self.accept)
            acciones.addWidget(aceptar)
        contenido.addLayout(acciones)
        diseno_exterior.addLayout(contenido)


class TextInputDialog(QDialog):
    def __init__(self, titulo, mensaje, texto_inicial="", parent=None):
        super().__init__(parent)
        self.setObjectName("institutionalDialog")
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setStyleSheet(MODAL_STYLE)

        exterior = QVBoxLayout(self)
        exterior.setContentsMargins(0, 0, 0, 0)
        exterior.setSpacing(0)
        exterior.addWidget(
            preparar_ventana_sin_marco(self, titulo, controles_completos=False)
        )
        acento = QFrame()
        acento.setObjectName("dialogAccentInfo")
        acento.setFixedHeight(5)
        exterior.addWidget(acento)
        contenido = QVBoxLayout()
        contenido.setContentsMargins(24, 22, 24, 20)
        contenido.setSpacing(12)
        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("dialogTitle")
        mensaje_label = QLabel(mensaje)
        mensaje_label.setObjectName("dialogMessage")
        mensaje_label.setWordWrap(True)
        self.entrada = QLineEdit(texto_inicial)
        self.entrada.setObjectName("dialogInput")
        self.entrada.selectAll()
        self.entrada.returnPressed.connect(self.accept)
        contenido.addWidget(titulo_label)
        contenido.addWidget(mensaje_label)
        contenido.addWidget(self.entrada)
        acciones = QHBoxLayout()
        acciones.addStretch()
        cancelar = QPushButton("Cancelar")
        cancelar.setObjectName("dialogSecondaryButton")
        cancelar.clicked.connect(self.reject)
        guardar = QPushButton("Guardar")
        guardar.setObjectName("dialogPrimaryButton")
        guardar.clicked.connect(self.accept)
        acciones.addWidget(cancelar)
        acciones.addWidget(guardar)
        contenido.addLayout(acciones)
        exterior.addLayout(contenido)
        self.entrada.setFocus()


def ask_text(parent, titulo, mensaje, texto_inicial=""):
    dialogo = TextInputDialog(titulo, mensaje, texto_inicial, parent)
    confirmado = exec_modal(dialogo) == QDialog.Accepted
    return dialogo.entrada.text(), confirmado


def ask_confirmation(parent, titulo, mensaje, tipo="warning"):
    return exec_modal(MessageDialog(titulo, mensaje, tipo, True, parent)) == QDialog.Accepted


def show_error(parent, titulo, mensaje):
    exec_modal(MessageDialog(titulo, mensaje, "error", parent=parent))


def show_warning(parent, titulo, mensaje):
    exec_modal(MessageDialog(titulo, mensaje, "warning", parent=parent))


def show_info(parent, titulo, mensaje, success=False):
    exec_modal(
        MessageDialog(
            titulo, mensaje, "success" if success else "info", parent=parent
        )
    )


def exec_modal(dialogo):
    """Abre el diálogo con el bloqueo modal nativo y sin capas superpuestas."""
    return dialogo.exec()
