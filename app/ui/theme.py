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
    background-color: #F7F9FC;
    color: #0B2240;
    font-family: "Segoe UI";
}
QLabel#pageEyebrow { color: #1A5B9D; font-size: 9px; font-weight: 900; letter-spacing: 2px; }
QLabel#pageTitle { color: #071D38; font-size: 28px; font-weight: 800; }
QLabel#pageSubtitle { color: #68778B; font-size: 12px; }
QPushButton#pageBackButton {
    background: transparent; color: #174E89; border: none;
    padding: 7px 0; font-size: 12px; font-weight: 700;
}
QPushButton#pageBackButton:hover { color: #0A315D; }
QLabel#adminBadge {
    background-color: #E7F1FA; color: #0A4D91; border: 1px solid #BDD3E8;
    border-radius: 3px; padding: 6px 10px; font-size: 9px; font-weight: 800;
}
QFrame#statCard {
    background-color: #FFFFFF; border: 1px solid #DCE3EB;
    border-radius: 6px; min-height: 72px;
}
QLabel#statLabel { background: transparent; color: #617187; font-size: 12px; font-weight: 600; }
QLabel#statValue { background: transparent; color: #0B3158; font-size: 26px; font-weight: 800; }
QFrame#tableCard {
    background-color: #FFFFFF; border: 1px solid #DCE3EB; border-radius: 7px;
}
QLabel#tableSectionTitle { background: transparent; color: #123D68; font-size: 14px; font-weight: 800; }
QLabel#tableSectionSubtitle { background: transparent; color: #748195; font-size: 10px; }
QLabel#directoryCount { color: #536A82; background: #EEF3F8; border-radius: 3px; padding: 6px 9px; font-size: 10px; font-weight: 700; }
QLineEdit#searchInput {
    background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 3px;
    padding: 8px 12px; color: #16314F; font-size: 11px;
}
QLineEdit#searchInput:focus { border: 2px solid #1B63AF; padding: 7px 11px; }
QPushButton#primaryButton {
    background-color: #0A4D91; color: #FFFFFF; border: none; border-radius: 6px;
    padding: 11px 18px; font-size: 12px; font-weight: 800;
}
QPushButton#primaryButton:hover { background-color: #073A6F; }
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
QTableWidget#usersTable {
    background-color: #FFFFFF; border: none;
    color: #273E57; font-size: 12px; selection-background-color: #E7F1FA;
    selection-color: #0B3158; outline: none;
}
QTableWidget#usersTable::item { padding: 10px 14px; border-bottom: 1px solid #E8EDF2; }
QTableWidget#usersTable::item:hover { background-color: #F4F8FC; }
QWidget#cellWrapper { background-color: transparent; }
QLabel#usernameCell { background: transparent; color: #0A4D91; font-size: 12px; font-weight: 700; }
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
    background-color: #E7EDF3; color: #52657A; border: none;
    border-bottom: 1px solid #CBD5E1; padding: 12px; font-size: 10px; font-weight: 800;
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
QFrame#dashboardSidebar { background-color: #062F62; border: none; }
QLabel#sidebarUniversity { color: #FFFFFF; font-size: 10px; font-weight: 800; letter-spacing: 1px; }
QLabel#sidebarTitle { color: #FFFFFF; font-family: "Georgia"; font-size: 27px; font-weight: 700; }
QLabel#sidebarSubtitle { color: #B9C9DE; font-size: 12px; line-height: 1.4; }
QPushButton#navButton, QPushButton#activeNavButton, QPushButton#logoutNavButton {
    text-align: left; border: none; border-radius: 10px; padding: 10px 13px;
    color: #E4EDF8; background: transparent; font-size: 12px; font-weight: 500;
}
QPushButton#navButton:hover, QPushButton#logoutNavButton:hover { background-color: #0B3B70; color: #FFFFFF; }
QPushButton#activeNavButton { background-color: #1555A5; color: #FFFFFF; font-weight: 700; }
QLabel#sidebarAvatar { background-color: #547399; color: #FFFFFF; border-radius: 19px; font-weight: 700; }
QLabel#sidebarProfile { color: #FFFFFF; font-size: 11px; }
QWidget#dashboardContent { background-color: #F8FAFD; }
QLabel#dashboardSection { color: #183455; font-size: 12px; font-weight: 600; }
QLabel#dashboardUser { color: #142C49; font-size: 12px; font-weight: 600; }
QFrame#headerLine { background-color: #DDE3EB; border: none; }
QLabel#routeEyebrow { color: #285998; font-size: 10px; font-weight: 900; letter-spacing: 2px; }
QLabel#routeTitle { color: #061E49; font-family: "Segoe UI"; font-size: 34px; font-weight: 800; }
QLabel#routeSubtitle { color: #63728A; font-family: "Segoe UI"; font-size: 13px; font-weight: 400; }
QWidget#workflowPanel { background: transparent; }
QFrame#processCard { background-color: #FFFFFF; border: 1px solid #D7DFEA; border-radius: 18px; }
QFrame#processCard:hover { border: 1px solid #7FA8D8; background-color: #FFFFFF; }
QLabel#stepBadge { background-color: #1767C5; color: #FFFFFF; border-radius: 17px; font-size: 14px; font-weight: 800; }
QLabel#processIcon { background: transparent; }
QLabel#processTitle { color: #071F4D; font-size: 17px; font-weight: 800; }
QLabel#processDescription { color: #62728A; font-size: 12px; }
QPushButton#openModuleButton {
    background-color: #0B62CE; color: #FFFFFF; border: none;
    border-radius: 10px; padding: 10px 16px; font-size: 12px; font-weight: 800;
}
QPushButton#openModuleButton:hover { background-color: #084EA7; color: #FFFFFF; }
QLabel#dashboardFooter { color: #7D899A; font-size: 9px; }
"""


EXCEL_MODULE_STYLESHEET = """
QWidget#excelProcessPage {
    background-color: #F7F9FC; color: #0B2240; font-family: "Segoe UI";
}
QDialog#excelPreviewDialog, QDialog#optionManagementDialog {
    background-color: #FFFFFF; color: #0B2240; border: 2px solid #0B3F70;
    font-family: "Segoe UI";
}
QScrollArea#excelMainScroll, QWidget#excelScrollableContent {
    background-color: #F7F9FC; border: none;
}
QScrollArea#excelMainScroll QScrollBar:vertical {
    background: #EEF2F6; width: 10px; margin: 0;
}
QScrollArea#excelMainScroll QScrollBar::handle:vertical {
    background: #A9B8C8; min-height: 32px; border-radius: 5px;
}
QScrollArea#excelMainScroll QScrollBar::handle:vertical:hover { background: #7890AA; }
QScrollArea#excelMainScroll QScrollBar::add-line:vertical,
QScrollArea#excelMainScroll QScrollBar::sub-line:vertical { height: 0; }
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
    background-color: #FFFFFF; color: #174E89;
    border: 1px solid #D5DFEA; border-radius: 10px;
    padding: 8px 16px; text-align: center;
    font-size: 11px; font-weight: 800;
}
QPushButton#excelBackButton:hover {
    background-color: #EAF3FC; color: #0A4D91;
    border-color: #8EB4DA;
}
QPushButton#excelBackButton:pressed {
    background-color: #D9EAF9; color: #073A6F;
    border-color: #5E94C8;
}
QFrame#excelSetupCard, QFrame#excelStepRow {
    background: transparent; border: none;
}
QFrame#sourceFilesPanel {
    background-color: #F1F5F9; border-top: 1px solid #CBD5E1;
    border-bottom: 1px solid #CBD5E1;
}
QLabel#sourceFilesTitle { color: #274766; font-size: 10px; font-weight: 900; letter-spacing: 1px; }
QFrame#excelStepRow { border-bottom: 1px solid #D7E0E9; }
QFrame#excelStepRow:hover { background-color: #EDF4FB; }
QLabel#excelFieldLabel { color: #183455; font-size: 10px; font-weight: 800; }
QLabel#sequenceFieldLabel { color: #31516F; font-size: 9px; font-weight: 900; letter-spacing: 1px; }
QLabel#configurationSummary {
    color: #526A82; border-top: 1px solid #DCE3EA;
    padding-top: 8px; font-size: 10px; font-weight: 600;
}
QComboBox {
    background-color: #FFFFFF; color: #16314F; border: 1px solid #CDD6E1;
    border-radius: 7px; padding: 7px 38px 7px 11px; min-height: 22px; font-size: 11px;
}
QComboBox:focus { border: 2px solid #1B63AF; padding: 6px 37px 6px 10px; }
QComboBox:hover { border-color: #7FA7D2; background-color: #FBFDFF; }
QComboBox::drop-down {
    subcontrol-origin: padding; subcontrol-position: top right;
    width: 32px; border-left: 1px solid #E0E6ED;
    background-color: #F2F6FA; border-top-right-radius: 7px;
    border-bottom-right-radius: 7px;
}
QComboBox::drop-down:hover { background-color: #E7F1FA; }
QComboBox::down-arrow { width: 10px; height: 7px; }
QComboBox QAbstractItemView {
    background-color: #FFFFFF; color: #183455;
    border: 1px solid #BFCBDC; border-radius: 9px;
    padding: 6px; outline: 0px; font-size: 11px;
    selection-background-color: #E4EFFB;
    selection-color: #0A4D91;
}
QComboBox QAbstractItemView::item {
    min-height: 32px; padding: 5px 10px;
    border: none; border-radius: 6px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #F0F5FA; color: #0A4D91;
}
QComboBox QScrollBar:vertical {
    background: #F3F6F9; width: 9px; margin: 5px 2px 5px 0px;
    border: none; border-radius: 4px;
}
QComboBox QScrollBar::handle:vertical {
    background: #AFC0D3; min-height: 26px; border-radius: 4px;
}
QComboBox QScrollBar::add-line:vertical,
QComboBox QScrollBar::sub-line:vertical { height: 0px; }
QLabel#selectedCsvLabel {
    background-color: #FFFFFF; color: #68778B; border: 1px solid #CBD5E1;
    border-radius: 3px; padding: 8px 10px; font-size: 10px;
}
QLabel#destinationTitle { color: #164E87; font-size: 9px; font-weight: 900; padding-top: 3px; }
QLabel#destinationPath { color: #355B80; border-top: 1px solid #D6E0EA; padding-top: 6px; font-size: 10px; }
QFrame#excelStepsContainer {
    background-color: #FFFFFF; border: 1px solid #D7E0E9;
    border-top: none; border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}
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
QPushButton#loadedCsvButton {
    background-color: #E7F6ED; color: #137A45; border: 1px solid #9FD5B7;
    border-radius: 4px; padding: 9px 15px; font-size: 11px; font-weight: 800;
}
QPushButton#loadedCsvButton:hover { background-color: #DDF2E6; }
QPushButton#stepActionButton {
    background-color: #FFFFFF; color: #0A4D91; border: 1px solid #0A4D91;
}
QPushButton#stepActionButton:hover { background-color: #EAF3FC; }
QPushButton#secondaryExcelButton {
    background-color: #FFFFFF; color: #124C87; border: 1px solid #CDD8E4;
}
QPushButton#secondaryExcelButton:hover { background-color: #EDF4FB; }
QPushButton#addOptionButton {
    background-color: #FFFFFF; color: #0A4D91; border: 1px solid #0A4D91;
    border-radius: 3px; padding: 0; font-size: 17px; font-weight: 600;
}
QPushButton#addOptionButton:hover { background-color: #EAF3FC; }
QPushButton#addOptionButton:pressed { background-color: #D8EAFB; }
QPushButton#dangerOptionButton {
    background-color: transparent; color: #667085; border: 1px solid #D0D5DD;
    border-radius: 4px; padding: 9px 15px; font-size: 11px; font-weight: 700;
}
QPushButton#dangerOptionButton:hover { background-color: #FDEBEC; color: #B42332; border-color: #E9B8BE; }
QLabel#optionDialogTitle { color: #071D38; font-size: 20px; font-weight: 800; }
QLabel#optionDialogHelp { color: #66758A; font-size: 11px; }
QListWidget#optionList {
    background-color: #FFFFFF; color: #183455; border: 1px solid #CBD5E1;
    border-radius: 3px; padding: 4px; font-size: 11px;
}
QListWidget#optionList::item { padding: 9px 10px; border-bottom: 1px solid #EDF1F5; }
QListWidget#optionList::item:selected { background-color: #E7F1FA; color: #0A4D91; }
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
QWidget#userFormPage { background-color: #F7F9FC; color: #0B2240; font-family: "Segoe UI"; }
QLabel#formEyebrow { color: #1A5B9D; font-size: 9px; font-weight: 900; letter-spacing: 2px; }
QLabel#formPageTitle { color: #071D38; font-size: 27px; font-weight: 800; }
QLabel#formPageSubtitle { color: #68778B; font-size: 12px; }
QFrame#formCard { background: #FFFFFF; border: 1px solid #D7E0E9; border-radius: 7px; }
QLabel#formHelp { background-color: #EEF4FA; color: #405D79; border-left: 3px solid #0A4D91; padding: 11px 13px; font-size: 10px; }
QLabel#fieldLabel { color: #183455; font-size: 10px; font-weight: 800; }
QLineEdit, QComboBox {
    background-color: #FFFFFF; color: #16314F; border: 1px solid #CBD5E1;
    border-radius: 3px; padding: 0 12px; min-height: 42px; font-size: 11px;
}
QLineEdit:focus, QComboBox:focus { border: 2px solid #1B63AF; }
QCheckBox { color: #435A72; font-size: 11px; spacing: 9px; }
QLabel#formError { background: #FDEBEC; color: #B42332; border: 1px solid #E9B8BE; border-radius: 4px; padding: 10px 12px; font-size: 10px; }
QPushButton#backButton { background: transparent; color: #174E89; border: none; padding: 8px 0; font-size: 12px; font-weight: 700; }
QPushButton#backButton:hover { color: #0A315D; }
QPushButton#primaryButton {
    background-color: #0A4D91; color: white; border: none; border-radius: 6px;
    padding: 10px 17px; font-size: 11px; font-weight: 800;
}
QPushButton#primaryButton:hover { background-color: #073A6F; }
QPushButton#secondaryButton {
    background-color: #FFFFFF; color: #124C87; border: 1px solid #CDD8E4; border-radius: 6px;
    padding: 10px 17px; font-size: 11px; font-weight: 700;
}
QPushButton#secondaryButton:hover { background-color: #EDF4FB; }
"""
