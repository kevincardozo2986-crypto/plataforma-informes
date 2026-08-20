"""Estilos visuales compartidos por la aplicación."""

WHITE = "#FFFFFF"
BACKGROUND = "#F5F6FA"
TEXT = "#211568"
MUTED_TEXT = "#697087"
TURQUOISE = "#36BCE8"


LOGIN_STYLESHEET = """
QWidget#loginWindow {
    background-color: #F5F6FA;
    color: #211568;
    font-family: "Segoe UI";
}

QFrame#loginCard {
    background-color: #FFFFFF;
    border: 1px solid #E4E5EC;
    border-radius: 28px;
}

QFrame#heroPanel {
    background-color: #FBFBFC;
    border-top-left-radius: 27px;
    border-bottom-left-radius: 27px;
}

QLabel#universityLogo {
    background-color: transparent;
}

QLabel#brandName {
    color: #211568;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#reportTitle, QLabel#platformTitle {
    color: #211568;
    font-size: 36px;
    font-weight: 800;
}

QLabel#platformTitle {
    color: #FF5E70;
}

QLabel#tagline {
    color: #4F5265;
    font-size: 13px;
}

QLabel#benefitBadge {
    background-color: #FFFFFF;
    color: #FF5E70;
    border-radius: 26px;
    font-size: 13px;
    font-weight: 800;
}

QLabel#benefitText {
    color: #211568;
    font-size: 12px;
}

QLabel#studentImage {
    background-color: transparent;
}

QFrame#formPanel {
    background-color: #FFFFFF;
    border-top-right-radius: 27px;
    border-bottom-right-radius: 27px;
}

QLabel#formTitle {
    color: #211568;
    font-size: 34px;
    font-weight: 800;
}

QLabel#formSubtitle, QLabel#securityText {
    color: #73778A;
    font-size: 13px;
}

QLabel#securityText {
    font-size: 11px;
}

QLabel#fieldLabel {
    color: #211568;
    font-size: 12px;
    font-weight: 700;
}

QLineEdit {
    background-color: #FFFFFF;
    color: #211568;
    border: 1px solid #D8DAE3;
    border-radius: 11px;
    padding: 0 16px;
    font-size: 13px;
    selection-background-color: #36BCE8;
}

QLineEdit:hover {
    border-color: #8D95AB;
}

QLineEdit:focus {
    border: 2px solid #36BCE8;
    padding: 0 15px;
}

QLabel#errorLabel {
    background-color: #FFF0F3;
    color: #C53E56;
    border-radius: 8px;
    padding: 10px 12px;
    font-size: 11px;
}

QPushButton#loginButton {
    background-color: #FF5E70;
    color: #FFFFFF;
    border: none;
    border-radius: 11px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton#loginButton:hover {
    background-color: #ED4D60;
}

QPushButton#loginButton:pressed {
    background-color: #D94154;
}
"""


USERS_STYLESHEET = """
QWidget#usersPage {
    background-color: #F5F6FA;
    color: #211568;
    font-family: "Segoe UI";
}
QLabel#pageTitle { color: #211568; font-size: 30px; font-weight: 800; }
QLabel#pageSubtitle { color: #74798B; font-size: 13px; }
QPushButton#pageBackButton {
    background: transparent; color: #211568; border: none;
    padding: 7px 0; font-size: 12px; font-weight: 700;
}
QPushButton#pageBackButton:hover { color: #FF5E70; }
QLabel#adminBadge {
    background-color: #FFF0F3; color: #E64960; border-radius: 10px;
    padding: 7px 12px; font-size: 10px; font-weight: 800;
}
QFrame#statCard {
    background-color: #FFFFFF; border: 1px solid #E4E7EE;
    border-radius: 16px; min-height: 78px;
}
QLabel#statLabel { background: transparent; color: #697087; font-size: 13px; font-weight: 600; }
QLabel#statValue { background: transparent; color: #211568; font-size: 28px; font-weight: 800; }
QFrame#tableCard {
    background-color: #FFFFFF; border: 1px solid #E1E5EC; border-radius: 16px;
}
QLabel#tableSectionTitle { background: transparent; color: #211568; font-size: 15px; font-weight: 800; }
QLabel#tableSectionSubtitle { background: transparent; color: #7A8092; font-size: 11px; }
QLineEdit#searchInput {
    background-color: #F8F9FC; border: 1px solid #DDE1EA; border-radius: 18px;
    padding: 10px 16px; color: #211568; font-size: 13px;
}
QLineEdit#searchInput:focus { background: #FFFFFF; border: 2px solid #36BCE8; padding: 9px 13px; }
QPushButton#primaryButton {
    background-color: #FF5E70; color: #FFFFFF; border: none; border-radius: 9px;
    padding: 12px 20px; font-size: 13px; font-weight: 700;
}
QPushButton#primaryButton:hover { background-color: #EB4B5E; }
QPushButton#secondaryButton {
    background-color: #FFFFFF; color: #211568; border: 1px solid #D9DDE7;
    border-radius: 17px; padding: 9px 17px; font-size: 12px; font-weight: 600;
}
QPushButton#secondaryButton:hover { background-color: #F3F5FA; border-color: #BFC5D2; }
QPushButton#dangerButton {
    background-color: #FFF0F3; color: #D94154; border: none;
    border-radius: 17px; padding: 9px 17px; font-size: 12px; font-weight: 600;
}
QPushButton#dangerButton:hover { background-color: #FFDDE4; }
QTableWidget {
    background-color: #FFFFFF; border: none;
    color: #30364A; font-size: 13px; selection-background-color: #E8F6FC;
    selection-color: #211568; outline: none;
}
QTableWidget::item { padding: 10px 14px; border-bottom: 1px solid #F0F2F6; }
QTableWidget::item:hover { background-color: #F7FBFE; }
QWidget#cellWrapper { background-color: transparent; }
QLabel#usernameCell { background: transparent; color: #211568; font-size: 13px; font-weight: 700; }
QPushButton#rowEditButton, QPushButton#rowStatusButton, QPushButton#rowDeleteButton {
    border: none; border-radius: 19px; padding: 8px;
}
QPushButton#rowEditButton { background-color: #EDF4FF; color: #3569C8; }
QPushButton#rowEditButton:hover { background-color: #DCE9FF; }
QPushButton#rowStatusButton { background-color: #F2F0FF; color: #6654C7; }
QPushButton#rowStatusButton:hover { background-color: #E5E0FF; }
QPushButton#rowDeleteButton { background-color: #FFF0F3; color: #D94154; }
QPushButton#rowDeleteButton:hover { background-color: #FFDDE4; }
QHeaderView::section {
    background-color: #F7F8FB; color: #777D8E; border: none;
    border-bottom: 1px solid #E1E5EC; padding: 13px; font-size: 11px; font-weight: 800;
}
"""


DASHBOARD_STYLESHEET = """
QWidget#dashboardPage { background-color: #F5F6FA; color: #211568; font-family: "Segoe UI"; }
QLabel#dashboardUniversity { background: transparent; color: #211568; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#dashboardBrand { background: transparent; color: #211568; font-size: 22px; font-weight: 800; }
QLabel#dashboardGreeting { background: transparent; color: #4F566B; font-size: 13px; font-weight: 600; }
QLabel#dashboardRole { background-color: #FFF0F3; color: #D94154; border-radius: 11px; padding: 7px 12px; font-size: 10px; font-weight: 800; }
QPushButton#manageUsersButton, QPushButton#logoutButton { border-radius: 10px; padding: 10px 15px; font-size: 12px; font-weight: 700; }
QPushButton#manageUsersButton { background-color: #211568; color: white; border: none; }
QPushButton#manageUsersButton:hover { background-color: #38278E; }
QPushButton#logoutButton { background-color: white; color: #52596D; border: 1px solid #DDE1E9; }
QPushButton#logoutButton:hover { background-color: #FFF0F3; color: #D94154; border-color: #FFC8D1; }
QFrame#welcomePanel { background-color: #FFFFFF; border: 1px solid #E3E6ED; border-radius: 18px; }
QFrame#welcomeAccent { background-color: #FF5E70; border: none; border-radius: 3px; }
QLabel#welcomeEyebrow { background: transparent; color: #FF5E70; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#welcomeTitle { background: transparent; color: #211568; font-size: 28px; font-weight: 800; }
QLabel#welcomeSubtitle { background: transparent; color: #697087; font-size: 13px; }
QLabel#welcomeDecoration { background-color: #EAF8FD; color: #1599C5; border-radius: 16px; padding: 14px 20px; font-size: 11px; font-weight: 800; }
QFrame#moduleCard { background-color: white; border: 1px solid #E1E5EC; border-radius: 18px; }
QFrame#moduleCard:hover { border: 2px solid #CFEAF4; background-color: #FCFEFF; }
QLabel#moduleIcon { background-color: #EFF8FC; border-radius: 14px; }
QLabel#moduleEyebrow { background: transparent; color: #FF5E70; font-size: 9px; font-weight: 800; letter-spacing: 1px; }
QLabel#moduleTitle { background: transparent; color: #211568; font-size: 21px; font-weight: 800; }
QLabel#moduleDescription { background: transparent; color: #687086; font-size: 12px; }
QPushButton#excelModuleButton, QPushButton#reportModuleButton, QPushButton#historyModuleButton {
    border: none; border-radius: 10px; padding: 11px 18px; font-size: 12px; font-weight: 800;
}
QPushButton#excelModuleButton { background-color: #36BCE8; color: #15314A; }
QPushButton#excelModuleButton:hover { background-color: #20AEDD; color: white; }
QPushButton#reportModuleButton { background-color: #FF5E70; color: white; }
QPushButton#reportModuleButton:hover { background-color: #EB4B5E; }
QPushButton#historyModuleButton { background-color: #FFD21C; color: #493B00; }
QPushButton#historyModuleButton:hover { background-color: #F2C300; }
QLabel#dashboardFooter { background: transparent; color: #8A90A0; font-size: 10px; }
QFrame#dashboardSidebar {
    background-color: #FFFFFF; border: none; border-right: 1px solid #E5E7EE;
}
QLabel#sidebarUniversity {
    background: transparent; color: #211568; font-size: 10px; font-weight: 900; letter-spacing: 1px;
}
QLabel#sidebarTitle {
    background: transparent; color: #211568; font-size: 28px; font-weight: 900;
}
QLabel#sidebarSubtitle { background: transparent; color: #777D8E; font-size: 12px; }
QPushButton#sidebarUsersButton, QPushButton#sidebarLogoutButton {
    text-align: left; border-radius: 11px; padding: 12px 14px; font-size: 12px; font-weight: 700;
}
QPushButton#sidebarUsersButton { background-color: #211568; color: #FFFFFF; border: none; }
QPushButton#sidebarUsersButton:hover { background-color: #FF5E70; }
QPushButton#sidebarLogoutButton { background-color: #F5F6FA; color: #5F667A; border: none; }
QPushButton#sidebarLogoutButton:hover { background-color: #FFF0F3; color: #D94154; }
QWidget#dashboardContent { background: transparent; }
QLabel#dashboardSection { background: transparent; color: #8B91A0; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#dashboardGreetingPill {
    background-color: #FFFFFF; color: #211568; border: 1px solid #E4E6EC;
    border-radius: 15px; padding: 9px 16px; font-size: 12px; font-weight: 700;
}
QLabel#routeEyebrow { background: transparent; color: #FF5E70; font-size: 10px; font-weight: 900; letter-spacing: 2px; }
QLabel#routeTitle { background: transparent; color: #211568; font-size: 36px; font-weight: 900; }
QLabel#routeSubtitle { background: transparent; color: #6F7689; font-size: 14px; }
QWidget#workflowPanel, QWidget#processStep { background: transparent; }
QLabel#processTitle { background: transparent; color: #211568; font-size: 18px; font-weight: 900; }
QLabel#processDescription { background: transparent; color: #6E7588; font-size: 12px; }
QLabel#excelStepNumber, QLabel#reportStepNumber, QLabel#historyStepNumber {
    border-radius: 13px; font-size: 10px; font-weight: 900;
}
QLabel#excelStepNumber { background-color: #E8F8FD; color: #1599C5; }
QLabel#reportStepNumber { background-color: #FFF0F3; color: #E34C61; }
QLabel#historyStepNumber { background-color: #FFF8D8; color: #A98400; }
QPushButton#excelCircleButton, QPushButton#reportCircleButton, QPushButton#historyCircleButton {
    border: 7px solid #FFFFFF; border-radius: 52px;
}
QPushButton#excelCircleButton { background-color: #36BCE8; }
QPushButton#excelCircleButton:hover { background-color: #20AEDD; border-color: #DDF6FD; }
QPushButton#reportCircleButton { background-color: #FF5E70; }
QPushButton#reportCircleButton:hover { background-color: #EB4B5E; border-color: #FFE2E7; }
QPushButton#historyCircleButton { background-color: #FFD21C; }
QPushButton#historyCircleButton:hover { background-color: #F2C300; border-color: #FFF5C2; }
QLabel#excelProcessHint, QLabel#reportProcessHint, QLabel#historyProcessHint {
    background: transparent; font-size: 11px; font-weight: 800;
}
QLabel#excelProcessHint { color: #1599C5; }
QLabel#reportProcessHint { color: #E34C61; }
QLabel#historyProcessHint { color: #A98400; }
QFrame#flowStatus { background-color: rgba(255, 255, 255, 210); border: 1px solid #E4E7ED; border-radius: 15px; }
QLabel#statusDot { background: transparent; color: #36BCE8; font-size: 13px; }
QLabel#statusText { background: transparent; color: #70778A; font-size: 11px; }
"""


USER_FORM_STYLESHEET = """
QWidget#userFormPage { background-color: #F5F6FA; color: #211568; font-family: "Segoe UI"; }
QLabel#formPageTitle { color: #211568; font-size: 27px; font-weight: 800; }
QLabel#formPageSubtitle { color: #74798B; font-size: 12px; }
QFrame#formCard { background: #FFFFFF; border: 1px solid #E1E5EC; border-radius: 14px; }
QLabel#fieldLabel { color: #30364A; font-size: 11px; font-weight: 700; }
QLineEdit, QComboBox {
    background-color: #F9FAFC; color: #211568; border: 1px solid #DDE1EA;
    border-radius: 9px; padding: 0 13px; min-height: 44px; font-size: 12px;
}
QLineEdit:focus, QComboBox:focus { background: #FFFFFF; border: 2px solid #36BCE8; }
QCheckBox { color: #535A6E; font-size: 12px; spacing: 9px; }
QLabel#formError { background: #FFF0F3; color: #C53E56; border-radius: 8px; padding: 10px 12px; font-size: 11px; }
QPushButton#backButton { background: transparent; color: #211568; border: none; padding: 8px 0; font-size: 12px; font-weight: 700; }
QPushButton#backButton:hover { color: #FF5E70; }
QPushButton#primaryButton {
    background-color: #FF5E70; color: white; border: none; border-radius: 8px;
    padding: 10px 17px; font-size: 12px; font-weight: 700;
}
QPushButton#primaryButton:hover { background-color: #EB4B5E; }
QPushButton#secondaryButton {
    background-color: #F3F5F9; color: #4E5568; border: none; border-radius: 8px;
    padding: 10px 17px; font-size: 12px; font-weight: 600;
}
QPushButton#secondaryButton:hover { background-color: #E7EAF0; }
"""
