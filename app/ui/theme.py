"""Estilos visuales compartidos por la aplicación."""

WHITE = "#FFFFFF"
BACKGROUND = "#F5F6FA"
TEXT = "#211568"
MUTED_TEXT = "#697087"
TURQUOISE = "#36BCE8"


LOGIN_STYLESHEET = """
QWidget#loginWindow {
    background-color: #F7F9FC;
    color: #071D38;
    font-family: "Segoe UI";
}

QFrame#loginCard {
    background-color: #FFFFFF;
    border: 1px solid #DCE3EB;
    border-radius: 28px;
}

QFrame#heroPanel {
    background-color: #F8FBFE;
    border-top-left-radius: 27px;
    border-bottom-left-radius: 27px;
}

QLabel#universityLogo {
    background-color: transparent;
}

QLabel#brandName {
    color: #0B315B;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#reportTitle, QLabel#platformTitle {
    color: #071D38;
    font-size: 36px;
    font-weight: 800;
}

QLabel#platformTitle {
    color: #0A4D91;
}

QLabel#tagline {
    color: #5D7087;
    font-size: 13px;
}

QLabel#benefitBadge {
    background-color: #FFFFFF;
    color: #0A4D91;
    border: 1px solid #D5E2EF;
    border-radius: 26px;
    font-size: 13px;
    font-weight: 800;
}

QLabel#benefitText {
    color: #183455;
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
    color: #071D38;
    font-size: 34px;
    font-weight: 800;
}

QLabel#formSubtitle, QLabel#securityText {
    color: #69798D;
    font-size: 13px;
}

QLabel#securityText {
    font-size: 11px;
}

QLabel#fieldLabel {
    color: #183455;
    font-size: 12px;
    font-weight: 700;
}

QLineEdit {
    background-color: #FFFFFF;
    color: #102A49;
    border: 1px solid #CDD7E2;
    border-radius: 11px;
    padding: 0 16px;
    font-size: 13px;
    selection-background-color: #2B72B7;
}

QLineEdit:hover {
    border-color: #7594B6;
}

QLineEdit:focus {
    border: 2px solid #1972C8;
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
    background-color: #0A4D91;
    color: #FFFFFF;
    border: none;
    border-radius: 11px;
    font-size: 13px;
    font-weight: 700;
}

QPushButton#loginButton:hover {
    background-color: #073D75;
}

QPushButton#loginButton:pressed {
    background-color: #052B55;
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

/* Dashboard institucional */
QWidget#dashboardPage { background-color: #F7F9FC; color: #0B2240; font-family: "Segoe UI"; }
QFrame#dashboardSidebar { background-color: #052B55; border: none; }
QLabel#sidebarUniversity { color: #FFFFFF; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#sidebarTitle { color: #FFFFFF; font-family: "Georgia"; font-size: 25px; font-weight: 700; }
QLabel#sidebarSubtitle { color: #C0CDE0; font-size: 12px; line-height: 1.4; }
QPushButton#navButton, QPushButton#activeNavButton, QPushButton#logoutNavButton {
    text-align: left; border: none; border-radius: 9px; padding: 9px 12px;
    color: #DDE7F4; background: transparent; font-size: 12px; font-weight: 500;
}
QPushButton#navButton:hover, QPushButton#logoutNavButton:hover { background-color: #0B3B70; color: #FFFFFF; }
QPushButton#activeNavButton { background-color: #114A89; color: #FFFFFF; font-weight: 700; }
QLabel#sidebarAvatar { background-color: #547399; color: #FFFFFF; border-radius: 19px; font-weight: 700; }
QLabel#sidebarProfile { color: #FFFFFF; font-size: 11px; }
QWidget#dashboardContent { background-color: #F9FBFE; }
QLabel#dashboardSection { color: #183455; font-size: 12px; font-weight: 600; }
QLabel#dashboardUser { color: #142C49; font-size: 12px; font-weight: 600; }
QFrame#headerLine { background-color: #DDE3EB; border: none; }
QLabel#routeEyebrow { color: #285998; font-size: 10px; font-weight: 900; letter-spacing: 2px; }
QLabel#routeTitle { color: #071D38; font-family: "Segoe UI"; font-size: 31px; font-weight: 700; }
QLabel#routeSubtitle { color: #66758A; font-family: "Segoe UI"; font-size: 13px; font-weight: 400; }
QWidget#workflowPanel { background: transparent; }
QFrame#processCard { background-color: #FFFFFF; border: 1px solid #DAE0E8; border-radius: 7px; }
QFrame#processCard:hover { border: 1px solid #8DA7C7; background-color: #FCFDFF; }
QLabel#stepBadge { background-color: #062F60; color: #FFFFFF; border-radius: 6px; font-size: 12px; font-weight: 800; }
QLabel#processIcon { background: transparent; }
QLabel#processTitle { color: #0B2240; font-size: 16px; font-weight: 800; }
QLabel#processDescription { color: #647286; font-size: 11px; }
QPushButton#openModuleButton {
    background-color: #FFFFFF; color: #06449A; border: 1px solid #E1E6ED;
    border-radius: 6px; padding: 8px 14px; font-size: 11px; font-weight: 800;
}
QPushButton#openModuleButton:hover { background-color: #06449A; color: #FFFFFF; border-color: #06449A; }
QLabel#dashboardFooter { color: #7D899A; font-size: 9px; }
"""


EXCEL_MODULE_STYLESHEET = """
QWidget#excelProcessPage, QDialog#excelPreviewDialog {
    background-color: #F7F9FC; color: #0B2240; font-family: "Segoe UI";
}
QFrame#excelHero {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #FFFFFF, stop:0.78 #F4F8FC, stop:1 #E7F0F9);
    border: none; border-radius: 10px;
}
QLabel#excelHeroImage { background: transparent; border: none; }
QLabel#excelPageTitle { color: #071D38; font-family: "Segoe UI"; font-size: 29px; font-weight: 700; }
QLabel#excelPageSubtitle { color: #68778B; font-family: "Segoe UI"; font-size: 13px; font-weight: 400; }
QLabel#excelEyebrow { color: #1A5B9D; font-size: 9px; font-weight: 900; letter-spacing: 2px; }
QFrame#excelSectionHeader { background: transparent; border: none; }
QLabel#sectionNumber {
    background-color: #07427E; color: #FFFFFF; border-radius: 2px;
    font-size: 12px; font-weight: 900;
}
QLabel#excelSectionTitle { background: transparent; color: #124A83; font-size: 13px; font-weight: 800; }
QPushButton#excelBackButton {
    background: transparent; color: #174E89; border: none; padding: 7px 0;
    text-align: left; font-size: 12px; font-weight: 700;
}
QPushButton#excelBackButton:hover { color: #0A315D; }
QFrame#excelSetupCard, QFrame#excelStepRow {
    background: transparent; border: none;
}
QFrame#excelStepRow { border-bottom: 1px solid #D7E0E9; }
QFrame#excelStepRow:hover { background-color: #EDF4FB; }
QLabel#excelFieldLabel { color: #183455; font-size: 10px; font-weight: 800; }
QComboBox {
    background-color: #FFFFFF; color: #16314F; border: 1px solid #CDD6E1;
    border-radius: 7px; padding: 8px 11px; min-height: 20px; font-size: 11px;
}
QComboBox:focus { border: 1px solid #1B63AF; }
QLabel#selectedCsvLabel {
    background-color: #F5F8FB; color: #68778B; border: 1px solid #E0E6ED;
    border-radius: 7px; padding: 9px 11px; font-size: 10px;
}
QFrame#destinationPreview {
    background-color: #E7F1FA; border: none; border-radius: 7px;
}
QLabel#destinationTitle { color: #164E87; font-size: 10px; font-weight: 900; }
QLabel#destinationPath { color: #355B80; font-size: 10px; }
QScrollArea#excelStepsScroll { background: transparent; border: none; }
QScrollArea#excelStepsScroll > QWidget > QWidget { background: transparent; }
QLabel#excelStepTitle { color: #102A49; font-size: 12px; font-weight: 800; }
QLabel#excelStepDescription { color: #748195; font-size: 10px; }
QFrame#stepsColumnsHeader { background-color: #E7EDF3; border: none; }
QLabel#stepsColumnLabel { color: #59697B; font-size: 9px; font-weight: 800; }
QLabel#pendingStepBadge, QLabel#availableStepBadge, QLabel#completedStepBadge, QLabel#errorStepBadge {
    border-radius: 18px; font-size: 13px; font-weight: 900;
}
QLabel#pendingStepBadge { background-color: #F0F3F7; color: #8B97A8; }
QLabel#availableStepBadge { background-color: #E9F2FC; color: #175DA7; }
QLabel#completedStepBadge { background-color: #E5F7ED; color: #16824B; }
QLabel#errorStepBadge { background-color: #FDEBEC; color: #C13949; }
QLabel#pendingStepStatus, QLabel#availableStepStatus, QLabel#completedStepStatus, QLabel#errorStepStatus {
    font-size: 10px; font-weight: 700;
}
QLabel#pendingStepStatus { color: #8B97A8; }
QLabel#availableStepStatus { color: #175DA7; }
QLabel#completedStepStatus { color: #16824B; }
QLabel#errorStepStatus { color: #C13949; }
QPushButton#stepActionButton, QPushButton#primaryExcelButton, QPushButton#secondaryExcelButton {
    border-radius: 7px; padding: 9px 15px; font-size: 11px; font-weight: 800;
}
QPushButton#primaryExcelButton {
    background-color: #0A4D91; color: #FFFFFF; border: none;
}
QPushButton#primaryExcelButton:hover { background-color: #073A6F; }
QPushButton#stepActionButton {
    background-color: #FFFFFF; color: #0A4D91; border: 1px solid #0A4D91;
}
QPushButton#stepActionButton:hover { background-color: #EAF3FC; }
QPushButton#secondaryExcelButton {
    background-color: #FFFFFF; color: #124C87; border: 1px solid #CDD8E4;
}
QPushButton#secondaryExcelButton:hover { background-color: #EDF4FB; }
QPushButton:disabled { background-color: #E9EDF2; color: #9AA4B2; border-color: #E0E5EB; }
QLabel#excelFeedback { color: #617187; font-size: 10px; }
QProgressBar#excelProgressBar {
    background-color: #DDE6F0; border: none; border-radius: 4px;
}
QProgressBar#excelProgressBar::chunk {
    background-color: #1972C8; border-radius: 4px;
}
QTabWidget#previewTabs::pane { background-color: #FFFFFF; border: 1px solid #DCE3EB; border-radius: 7px; }
QTabBar::tab { background: #EAF0F6; color: #50637A; padding: 9px 14px; margin-right: 2px; }
QTabBar::tab:selected { background: #0A4D91; color: #FFFFFF; }
QLabel#previewInfo { color: #52657C; font-size: 10px; font-weight: 700; }
QTableWidget#excelPreviewTable {
    background-color: #FFFFFF; alternate-background-color: #F6F9FC;
    color: #243B55; border: 1px solid #E0E6ED; gridline-color: #E7EBF0; font-size: 10px;
}
QTableWidget#excelPreviewTable::item { padding: 5px; }
QHeaderView::section {
    background-color: #0A3A6B; color: #FFFFFF; border: none;
    border-right: 1px solid #315A82; padding: 7px; font-size: 10px; font-weight: 700;
}
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
