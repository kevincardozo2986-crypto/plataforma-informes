import sys

from PySide6.QtWidgets import QApplication

from app.services.auth_service import initialize_auth
from app.ui.dashboard_window import DashboardWindow
from app.ui.login_window import LoginWindow


def main():
    initialize_auth()
    app = QApplication(sys.argv)

    login = LoginWindow()

    def close_dashboard(dashboard):
        login.usuario_input.clear()
        login.password_input.clear()
        login.showMaximized()
        login.raise_()
        login.activateWindow()
        dashboard.close()
        app.dashboard = None

    def open_dashboard(user):
        dashboard = DashboardWindow(user)
        app.dashboard = dashboard
        dashboard.logout_requested.connect(lambda: close_dashboard(dashboard))
        dashboard.showMaximized()
        login.hide()

    login.authentication_succeeded.connect(open_dashboard)
    login.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
