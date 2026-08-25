from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.user_service import (
    create_managed_user,
    delete_user,
    list_users,
    update_user,
)
from app.ui.user_form_widget import UserFormWidget
from app.ui.modal_dialogs import ask_confirmation, show_error, show_warning
from app.ui.theme import USERS_STYLESHEET


class AnimatedIconButton(QPushButton):
    """Botón de acción con una microanimación discreta al pasar el cursor."""

    def __init__(self):
        super().__init__()
        self.setIconSize(QSize(17, 17))
        self._animation = QPropertyAnimation(self, b"iconSize", self)
        self._animation.setDuration(140)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

    def _animate_to(self, size):
        self._animation.stop()
        self._animation.setStartValue(self.iconSize())
        self._animation.setEndValue(QSize(size, size))
        self._animation.start()

    def enterEvent(self, event):
        self._animate_to(21)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(17)
        super().leaveEvent(event)


class UsersPage(QWidget):
    """Pantalla administrativa para gestionar las cuentas del sistema."""

    back_requested = Signal()

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.users = []

        self.setMinimumSize(1050, 680)
        self._build_ui()
        self.setStyleSheet(USERS_STYLESHEET)
        self._load_users()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        self.list_page = QWidget()
        self.list_page.setObjectName("usersPage")
        page = QVBoxLayout(self.list_page)
        page.setContentsMargins(36, 26, 36, 30)
        page.setSpacing(16)

        back_button = QPushButton("←  Volver")
        back_button.setObjectName("pageBackButton")
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.back_requested.emit)

        page.addWidget(back_button, alignment=Qt.AlignLeft)
        page.addLayout(self._create_header())
        page.addLayout(self._create_stats())
        page.addWidget(self._create_table_card(), 1)

        self.form_page = UserFormWidget()
        self.form_page.back_requested.connect(self._show_list)
        self.form_page.save_requested.connect(self._save_form)
        self.stack.addWidget(self.list_page)
        self.stack.addWidget(self.form_page)
        root.addWidget(self.stack)

    def _create_header(self):
        header = QHBoxLayout()
        header.setSpacing(14)

        logo = QLabel()
        logo_path = Path(__file__).parent / "assets" / "usta-crest.png"
        logo.setPixmap(
            QPixmap(str(logo_path)).scaled(
                52, 52, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        logo.setFixedSize(56, 56)

        heading = QVBoxLayout()
        heading.setSpacing(3)
        eyebrow = QLabel("ADMINISTRACIÓN · CONTROL DE ACCESO")
        eyebrow.setObjectName("pageEyebrow")
        title = QLabel("Gestión de usuarios")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Administra las cuentas y permisos de acceso al sistema")
        subtitle.setObjectName("pageSubtitle")
        heading.addWidget(eyebrow)
        heading.addWidget(title)
        heading.addWidget(subtitle)

        admin_badge = QLabel("ACCESO ADMINISTRADOR")
        admin_badge.setObjectName("adminBadge")

        new_button = QPushButton("＋  Nuevo usuario")
        new_button.setObjectName("primaryButton")
        new_button.setCursor(Qt.PointingHandCursor)
        new_button.clicked.connect(self._create_user)

        header.addWidget(logo)
        header.addLayout(heading)
        header.addSpacing(10)
        header.addWidget(admin_badge)
        header.addStretch()
        header.addWidget(new_button)
        return header

    def _create_stats(self):
        stats = QHBoxLayout()
        stats.setSpacing(14)
        self.total_value, total_card = self._stat_card("Usuarios registrados", "#0A4D91")
        self.active_value, active_card = self._stat_card("Usuarios activos", "#16824B")
        self.admin_value, admin_card = self._stat_card("Administradores", "#D49A00")
        stats.addWidget(total_card)
        stats.addWidget(active_card)
        stats.addWidget(admin_card)
        return stats

    def _stat_card(self, label, color):
        card = QFrame()
        card.setObjectName("statCard")
        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)

        accent = QFrame()
        accent.setFixedSize(12, 12)
        accent.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        text = QLabel(label)
        text.setObjectName("statLabel")
        value = QLabel("0")
        value.setObjectName("statValue")

        layout.addWidget(accent)
        layout.addSpacing(5)
        layout.addWidget(text)
        layout.addStretch()
        layout.addWidget(value)
        return value, card

    def _create_table_card(self):
        card = QFrame()
        card.setObjectName("tableCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(20, 16, 20, 16)
        toolbar.setSpacing(14)

        table_heading = QVBoxLayout()
        table_heading.setSpacing(2)
        table_title = QLabel("Directorio de usuarios")
        table_title.setObjectName("tableSectionTitle")
        table_subtitle = QLabel("Consulta y administra las cuentas registradas")
        table_subtitle.setObjectName("tableSectionSubtitle")
        table_heading.addWidget(table_title)
        table_heading.addWidget(table_subtitle)

        self.directory_count = QLabel("0 registros")
        self.directory_count.setObjectName("directoryCount")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Buscar usuario, nombre o rol")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(360)
        self.search_input.setFixedHeight(40)
        self.search_input.textChanged.connect(self._filter_table)

        toolbar.addLayout(table_heading)
        toolbar.addStretch()
        toolbar.addWidget(self.directory_count)
        toolbar.addWidget(self.search_input)
        layout.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setObjectName("usersTable")
        self.table.setHorizontalHeaderLabels(
            ["USUARIO", "NOMBRE COMPLETO", "ROL", "ESTADO", "CREADO", "ACCIONES"]
        )
        self.table.verticalHeader().hide()
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 190)
        self.table.setColumnWidth(5, 160)

        layout.addWidget(self.table)
        return card

    def _load_users(self):
        try:
            self.users = list_users(self.current_user)
        except (PermissionError, ValueError) as error:
            show_error(self, "Acceso denegado", str(error))
            self.close()
            return

        self.table.setRowCount(len(self.users))
        for row, user in enumerate(self.users):
            # El contenido visible lo dibuja _user_cell. El item queda vacío
            # para conservar el identificador sin duplicar el texto.
            user_item = QTableWidgetItem("")
            user_item.setData(Qt.UserRole, user["id"])
            self.table.setItem(row, 0, user_item)
            self.table.setCellWidget(row, 0, self._user_cell(user))

            self.table.setItem(row, 1, QTableWidgetItem(user["full_name"]))

            role_text = "Administrador" if user["role"] == "admin" else "Usuario"
            role_item = QTableWidgetItem("")
            role_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, role_item)
            self.table.setCellWidget(
                row, 2, self._badge_cell(
                    role_text,
                    "#FFF0F3" if user["role"] == "admin" else "#EDF4FF",
                    "#D94154" if user["role"] == "admin" else "#3569C8",
                )
            )

            status_text = "Activo" if user["is_active"] else "Inactivo"
            status_item = QTableWidgetItem("")
            status_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, status_item)
            self.table.setCellWidget(
                row, 3, self._badge_cell(
                    status_text,
                    "#EAF9F5" if user["is_active"] else "#F1F2F5",
                    "#178A68" if user["is_active"] else "#73798A",
                )
            )

            date_item = QTableWidgetItem(user["created_at"])
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 4, date_item)
            self.table.setCellWidget(row, 5, self._actions_cell(user))
            self.table.setRowHeight(row, 70)

        self.total_value.setText(str(len(self.users)))
        self.active_value.setText(str(sum(user["is_active"] for user in self.users)))
        self.admin_value.setText(
            str(sum(user["role"] == "admin" for user in self.users))
        )
        self.directory_count.setText(f"{len(self.users)} registros")
        self._filter_table(self.search_input.text())

    def _user_cell(self, user):
        wrapper = QWidget()
        wrapper.setObjectName("cellWrapper")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(12, 6, 8, 6)
        layout.setSpacing(11)

        initials = "".join(
            part[0].upper() for part in user["full_name"].split()[:2] if part
        ) or user["username"][:2].upper()
        colors = ("#36BCE8", "#FF5E70", "#F2B705", "#6E5AE6")
        color = colors[user["id"] % len(colors)]

        avatar = QLabel(initials)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(42, 42)
        avatar.setStyleSheet(
            f"background-color: {color}; color: white; border-radius: 21px; "
            "font-size: 11px; font-weight: 800;"
        )
        username = QLabel(user["username"])
        username.setObjectName("usernameCell")

        layout.addWidget(avatar)
        layout.addWidget(username)
        layout.addStretch()
        return wrapper

    def _badge_cell(self, text, background, color):
        wrapper = QWidget()
        wrapper.setObjectName("cellWrapper")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(8, 10, 8, 10)
        layout.setAlignment(Qt.AlignCenter)

        badge = QLabel(text)
        badge.setAlignment(Qt.AlignCenter)
        badge.setMinimumWidth(72)
        badge.setStyleSheet(
            f"background-color: {background}; color: {color}; border-radius: 12px; "
            "padding: 6px 13px; font-size: 11px; font-weight: 700;"
        )
        layout.addWidget(badge)
        return wrapper

    def _actions_cell(self, user):
        wrapper = QWidget()
        wrapper.setObjectName("cellWrapper")
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignCenter)

        assets = Path(__file__).parent / "assets"

        edit_button = AnimatedIconButton()
        edit_button.setObjectName("rowEditButton")
        edit_button.setIcon(QIcon(str(assets / "edit.svg")))
        edit_button.setFixedSize(38, 38)
        edit_button.setToolTip("Editar usuario")
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.clicked.connect(
            lambda checked=False, selected=user: self._edit_user(selected)
        )

        status_button = AnimatedIconButton()
        status_button.setObjectName("rowStatusButton")
        status_button.setIcon(QIcon(str(assets / "power.svg")))
        status_button.setFixedSize(38, 38)
        status_button.setIconSize(edit_button.iconSize())
        status_button.setToolTip("Desactivar usuario" if user["is_active"] else "Activar usuario")
        status_button.setCursor(Qt.PointingHandCursor)
        status_button.clicked.connect(
            lambda checked=False, selected=user: self._toggle_user(selected)
        )

        delete_button = AnimatedIconButton()
        delete_button.setObjectName("rowDeleteButton")
        delete_button.setIcon(QIcon(str(assets / "trash.svg")))
        delete_button.setFixedSize(38, 38)
        delete_button.setIconSize(edit_button.iconSize())
        delete_button.setToolTip("Eliminar usuario")
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.clicked.connect(
            lambda checked=False, selected=user: self._delete_user(selected)
        )

        layout.addWidget(edit_button)
        layout.addWidget(status_button)
        layout.addWidget(delete_button)
        return wrapper

    def _filter_table(self, search_text):
        search_text = search_text.strip().lower()
        for row, user in enumerate(self.users):
            searchable = f"{user['username']} {user['full_name']} {user['role']}".lower()
            self.table.setRowHidden(row, search_text not in searchable)

    def _create_user(self):
        self.form_page.start_create()
        self.stack.setCurrentWidget(self.form_page)

    def _edit_user(self, user):
        self.form_page.start_edit(user)
        self.stack.setCurrentWidget(self.form_page)

    def _save_form(self, values):
        try:
            if self.form_page.user is None:
                create_managed_user(
                    self.current_user,
                    values["username"],
                    values["password"],
                    values["full_name"],
                    values["role"],
                )
            else:
                update_user(
                    self.current_user,
                    self.form_page.user["id"],
                    **values,
                )
        except (PermissionError, ValueError) as error:
            self.form_page.show_error(str(error))
            return

        self._load_users()
        self._show_list()

    def _show_list(self):
        self.stack.setCurrentWidget(self.list_page)

    def _toggle_user(self, user):
        try:
            update_user(
                self.current_user,
                user["id"],
                user["username"],
                user["full_name"],
                user["role"],
                not user["is_active"],
            )
            self._load_users()
        except (PermissionError, ValueError) as error:
            show_warning(self, "No se pudo cambiar el estado", str(error))

    def _delete_user(self, user):
        confirmado = ask_confirmation(
            self,
            "Eliminar usuario",
            f"¿Eliminar definitivamente a {user['username']}?",
        )
        if not confirmado:
            return

        try:
            delete_user(self.current_user, user["id"])
            self._load_users()
        except (PermissionError, ValueError) as error:
            show_warning(self, "No se pudo eliminar", str(error))
