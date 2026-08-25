import sys
import traceback
from pathlib import Path

from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication

from app.services.auth_service import initialize_auth
from app.ui.dashboard_window import DashboardWindow
from app.ui.login_window import LoginWindow
from app.ui.modal_dialogs import show_error


def main():
    initialize_auth()
    aplicacion = QApplication(sys.argv)
    aplicacion.setStyle("Fusion")
    paleta = QPalette()
    paleta.setColor(QPalette.Window, QColor("#F7F9FC"))
    paleta.setColor(QPalette.WindowText, QColor("#0B2240"))
    paleta.setColor(QPalette.Base, QColor("#FFFFFF"))
    paleta.setColor(QPalette.AlternateBase, QColor("#F1F5F9"))
    paleta.setColor(QPalette.ToolTipBase, QColor("#FFFFFF"))
    paleta.setColor(QPalette.ToolTipText, QColor("#16314F"))
    paleta.setColor(QPalette.Text, QColor("#16314F"))
    paleta.setColor(QPalette.Button, QColor("#FFFFFF"))
    paleta.setColor(QPalette.ButtonText, QColor("#173653"))
    paleta.setColor(QPalette.Highlight, QColor("#0A4D91"))
    paleta.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    paleta.setColor(QPalette.PlaceholderText, QColor("#7A8998"))
    paleta.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#7F8C99"))
    paleta.setColor(QPalette.Disabled, QPalette.Text, QColor("#7F8C99"))
    paleta.setColor(QPalette.Disabled, QPalette.Button, QColor("#E8EDF2"))
    paleta.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#8794A2"))
    aplicacion.setPalette(paleta)
    aplicacion.setWindowIcon(
        QIcon(str(Path(__file__).parent / "app" / "ui" / "assets" / "usta-crest.png"))
    )

    def manejar_error_no_controlado(tipo_error, error, seguimiento):
        """Informa fallos inesperados sin cerrar toda la aplicación."""
        traceback.print_exception(tipo_error, error, seguimiento)
        if issubclass(tipo_error, KeyboardInterrupt):
            return sys.__excepthook__(tipo_error, error, seguimiento)
        try:
            show_error(
                None,
                "Ocurrió un error inesperado",
                f"{error}\n\nLa aplicación continuará abierta. Intenta nuevamente.",
            )
        except Exception:
            pass

    sys.excepthook = manejar_error_no_controlado

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
