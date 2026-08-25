import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.services.auth_service import initialize_auth
from app.ui.dashboard_window import DashboardWindow
from app.ui.login_window import LoginWindow


def main():
    initialize_auth()
    aplicacion = QApplication(sys.argv)
    aplicacion.setWindowIcon(
        QIcon(str(Path(__file__).parent / "app" / "ui" / "assets" / "usta-crest.png"))
    )

    ventana_login = LoginWindow()

    def close_dashboard(ventana_dashboard):
        ventana_login.usuario_input.clear()
        ventana_login.password_input.clear()
        ventana_login.showMaximized()
        ventana_login.raise_()
        ventana_login.activateWindow()
        ventana_dashboard.close()
        aplicacion.dashboard = None

    def open_dashboard(usuario):
        ventana_dashboard = DashboardWindow(usuario)
        aplicacion.dashboard = ventana_dashboard
        ventana_dashboard.logout_requested.connect(
            lambda: close_dashboard(ventana_dashboard)
        )
        ventana_dashboard.showMaximized()
        ventana_login.hide()

    ventana_login.authentication_succeeded.connect(open_dashboard)
    ventana_login.showMaximized()

    sys.exit(aplicacion.exec())


if __name__ == "__main__":
    main()
