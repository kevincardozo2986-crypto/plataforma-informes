from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QWidget,
)

from app.ui.theme import USER_FORM_STYLESHEET


class UserFormWidget(QWidget):
    """Formulario integrado para crear o editar usuarios."""

    save_requested = Signal(dict)
    back_requested = Signal()

    def __init__(self):
        super().__init__()
        self.user = None
        self.setObjectName("userFormPage")
        self._build_ui()
        self.setStyleSheet(USER_FORM_STYLESHEET)

    def _build_ui(self):
        page = QVBoxLayout(self)
        page.setContentsMargins(42, 32, 42, 38)
        page.setSpacing(0)

        back_button = QPushButton("←  Volver a usuarios")
        back_button.setObjectName("backButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.back_requested.emit)

        self.title = QLabel()
        self.title.setObjectName("formPageTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("formPageSubtitle")

        card = QFrame()
        card.setObjectName("formCard")
        card.setMaximumWidth(760)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(34, 30, 34, 30)
        card_layout.setSpacing(0)

        self.username_input = self._field("Nombre de usuario")
        self.full_name_input = self._field("Nombre completo")
        self.password_input = self._field("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.role_input = QComboBox()
        self.role_input.addItem("Usuario", "user")
        self.role_input.addItem("Administrador", "admin")
        self.role_input.setMinimumHeight(46)
        self.active_input = QCheckBox("Permitir que este usuario inicie sesión")

        self.error_label = QLabel()
        self.error_label.setObjectName("formError")
        self.error_label.setWordWrap(True)
        self.error_label.hide()

        actions = QHBoxLayout()
        actions.addStretch()
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("secondaryButton")
        self.save_button = QPushButton()
        self.save_button.setObjectName("primaryButton")
        cancel_button.clicked.connect(self.back_requested.emit)
        self.save_button.clicked.connect(self._submit)
        actions.addWidget(cancel_button)
        actions.addWidget(self.save_button)

        self._add_field(card_layout, "Usuario", self.username_input)
        self._add_field(card_layout, "Nombre completo", self.full_name_input)
        self._add_field(card_layout, "Contraseña", self.password_input)
        self._add_field(card_layout, "Rol", self.role_input)
        card_layout.addWidget(self.active_input)
        card_layout.addSpacing(18)
        card_layout.addWidget(self.error_label)
        card_layout.addSpacing(22)
        card_layout.addLayout(actions)

        page.addWidget(back_button, alignment=Qt.AlignLeft)
        page.addSpacing(28)
        page.addWidget(self.title)
        page.addSpacing(6)
        page.addWidget(self.subtitle)
        page.addSpacing(26)
        page.addWidget(card, alignment=Qt.AlignHCenter)
        page.addStretch()

    def _field(self, placeholder):
        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setMinimumHeight(46)
        field.textChanged.connect(self.clear_error)
        return field

    def _add_field(self, layout, text, field):
        label = QLabel(text)
        label.setObjectName("fieldLabel")
        layout.addWidget(label)
        layout.addSpacing(7)
        layout.addWidget(field)
        layout.addSpacing(18)

    def start_create(self):
        self.user = None
        self.title.setText("Crear nuevo usuario")
        self.subtitle.setText("Completa los datos para habilitar una cuenta en el sistema.")
        self.save_button.setText("Crear usuario")
        self.username_input.clear()
        self.full_name_input.clear()
        self.password_input.clear()
        self.password_input.setPlaceholderText("Contraseña obligatoria")
        self.role_input.setCurrentIndex(0)
        self.active_input.setChecked(True)
        self.clear_error()
        self.username_input.setFocus()

    def start_edit(self, user):
        self.user = user
        self.title.setText("Editar usuario")
        self.subtitle.setText(f"Actualiza la información de {user['username']}.")
        self.save_button.setText("Guardar cambios")
        self.username_input.setText(user["username"])
        self.full_name_input.setText(user["full_name"])
        self.password_input.clear()
        self.password_input.setPlaceholderText("Déjala vacía para conservarla")
        self.role_input.setCurrentIndex(self.role_input.findData(user["role"]))
        self.active_input.setChecked(user["is_active"])
        self.clear_error()
        self.full_name_input.setFocus()

    def _submit(self):
        username = self.username_input.text().strip()
        full_name = self.full_name_input.text().strip()
        password = self.password_input.text()
        if not username:
            return self.show_error("Ingresa un nombre de usuario.")
        if not full_name:
            return self.show_error("Ingresa el nombre completo.")
        if self.user is None and not password:
            return self.show_error("La contraseña es obligatoria para un usuario nuevo.")
        self.save_requested.emit({
            "username": username,
            "full_name": full_name,
            "password": password,
            "role": self.role_input.currentData(),
            "is_active": self.active_input.isChecked(),
        })

    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()

    def clear_error(self):
        self.error_label.hide()
