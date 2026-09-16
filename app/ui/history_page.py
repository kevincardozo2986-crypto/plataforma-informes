"""Dashboard del historial de procesos visible para el usuario actual."""
from pathlib import Path

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QColor, QDesktopServices, QPixmap, QIcon, QPainter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView,
)
from app.services.process_history_service import list_completed_processes, list_incomplete_processes
from app.ui.assistant import MascotButton, show_assistant
from app.ui.modal_dialogs import show_error


class HistoryPage(QWidget):
    back_requested = Signal()
    resume_requested = Signal(object)
    browse_requested = Signal()

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.records = []
        self.setObjectName('historyPage')
        self.setStyleSheet('''
            QWidget#historyPage { background: #F7F9FC; }
            QFrame#historySidebar { background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #092F59,stop:1 #15569A); }
            QFrame#historySidebar QLabel { color: white; }
            QPushButton#sideLink { background: transparent; color: #E3EEFC; border: none; text-align: left; padding: 14px 12px; }
            QPushButton#sideLink:hover { background: #165AB0; }
            QPushButton#sideLink:checked { background: #0B63CE; color: white; }
            QWidget#historyPage QLabel, QWidget#historyPage QPushButton,
            QWidget#historyPage QLineEdit, QWidget#historyPage QComboBox,
            QWidget#historyPage QTableWidget { font-family: "Segoe UI"; }
            QLabel { color: #173653; }
            QLabel#historyTitle { font-size: 28px; font-weight: 700; }
            QFrame#historyHero { background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #092F59,stop:1 #155CA2); border-radius: 16px; }
            QFrame#historyHero QLabel#historyTitle { color: white; }
            QLabel#heroHint { color: #DCEAF9; font-size: 12px; }
            QLabel#heroEyebrow { color: #F3CA65; font-size: 10px; font-weight: 700; }
            QFrame#historyRecords { background: white; border: 1px solid #DFE7F0; border-radius: 14px; }
            QLabel#recordsTitle { font-size: 17px; font-weight: 700; }
            QComboBox::drop-down { border: none; width: 22px; }
            QLabel#historyHint { color: #64748B; font-size: 12px; }
            QFrame#historyMetric { background: white; border: 1px solid #DAE4EF; border-radius: 12px; }
            QLabel#metricValue { color: #0C58A3; font-size: 30px; font-weight: 700; }
            QPushButton { background: white; color: #0B5DAC; border: 1px solid #C6D7E8; border-radius: 8px; padding: 10px 16px; }
            QPushButton:hover { background: #EAF3FD; }
            QPushButton#historyPrimary { background: #0B63CE; color: white; border: none; font-weight: 700; }
            QPushButton:disabled { background: #E8EDF3; color: #8B98A8; }
            QLineEdit, QComboBox { background: white; border: 1px solid #CDDBEA; border-radius: 8px; padding: 10px; color: #173653; }
            QTableWidget { background: white; alternate-background-color: #F7FAFE; border: none; color: #173653; font-size: 12px; }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected { background: #DCEBFC; color: #123C69; }
            QHeaderView::section { background: #EDF3FA; color: #344D69; padding: 12px; border: none; font-weight: 600; }
        ''')
        shell = QHBoxLayout(self)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)
        sidebar = QFrame(objectName='historySidebar')
        sidebar.setFixedWidth(184)
        side = QVBoxLayout(sidebar)
        side.setContentsMargins(16, 24, 16, 24)
        side.setSpacing(10)
        crest = QLabel()
        crest.setPixmap(QPixmap(str(Path(__file__).parent / 'assets' / 'usta-crest.png')).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        crest.setAlignment(Qt.AlignCenter)
        side.addWidget(crest)
        university = QLabel('UNIVERSIDAD\nSANTO TOMÁS')
        university.setAlignment(Qt.AlignCenter)
        university.setStyleSheet('font-size: 16px; font-weight: 600;')
        side.addWidget(university)
        side.addSpacing(24)
        self.side_links = []
        for label, index in (('Inicio', -1), ('Mis informes', 0), ('Terminados', 1), ('Seguimiento', 2)):
            link = QPushButton(label, objectName='sideLink')
            if index < 0:
                link.clicked.connect(self.back_requested.emit)
            else:
                link.setCheckable(True)
                link.clicked.connect(lambda checked=False, value=index: self.status.setCurrentIndex(value))
                self.side_links.append(link)
            side.addWidget(link)
        help_button = QPushButton('Ayuda de Tommy', objectName='sideLink')
        help_button.clicked.connect(lambda: show_assistant(self, 'historial'))
        side.addWidget(help_button)
        side.addStretch()
        motto = QLabel('Aquí se construye\ntu propósito.')
        motto.setWordWrap(True)
        motto.setStyleSheet('font-size: 19px; font-style: italic; color: #E7F0FC; padding-bottom: 18px;')
        side.addWidget(motto)
        shell.addWidget(sidebar)
        root = QVBoxLayout()
        shell.addLayout(root, 1)
        root.setContentsMargins(20, 16, 20, 18)
        root.setSpacing(14)
        nav = QHBoxLayout()
        heading = QVBoxLayout()
        heading.addWidget(QLabel('Plataforma de Informes USTA', objectName='recordsTitle'))
        heading.addWidget(QLabel('Gestión y seguimiento de informes académicos', objectName='historyHint'))
        nav.addLayout(heading)
        nav.addStretch()
        nav.addWidget(MascotButton('historial', self))
        user_label = QLabel(str(user.get('full_name') or user.get('username') or 'Usuario USTA'))
        user_label.setMaximumWidth(180)
        user_label.setWordWrap(True)
        nav.addWidget(user_label)
        root.addLayout(nav)
        hero = QFrame(objectName='historyHero')
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 10, 24, 10)
        hero_copy = QVBoxLayout()
        hero_copy.addWidget(QLabel('TUS INFORMES  /  SEGUIMIENTO', objectName='heroEyebrow'))
        title = QLabel('Cada informe,<br>a un paso de <span style="color:#F9C747">tus metas</span>', objectName='historyTitle')
        title.setWordWrap(True)
        hero_copy.addWidget(title)
        hint = QLabel('Encuentra tus archivos y continúa donde lo dejaste.', objectName='heroHint')
        hint.setWordWrap(True)
        hero_copy.addWidget(hint)
        hero_layout.addLayout(hero_copy, 1)
        illustration = QLabel()
        tommy = QPixmap(str(Path(__file__).parent / 'assets' / 'tomy-welcome-cutout.png'))
        illustration.setPixmap(tommy.copy(0, 0, tommy.width(), int(tommy.height()*.55)).scaled(180, 148, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        hero_layout.addWidget(illustration)
        root.addWidget(hero)
        metrics = QHBoxLayout()
        self.metrics = []
        for caption, color, icon in zip(('Procesos registrados', 'Excel terminados', 'Pendientes', 'Programas académicos'), ('#1866B5', '#138267', '#AC7519', '#6551B2'), ('history.svg', 'excel.svg', 'document.svg', 'users.svg')):
            card = QFrame(objectName='historyMetric')
            box = QVBoxLayout(card)
            box.setContentsMargins(14, 12, 14, 12)
            value = QLabel('0', objectName='metricValue')
            self.metrics.append(value)
            top = QHBoxLayout()
            value.setStyleSheet(f'color: {color};')
            mark = QLabel()
            icon_pixmap = QPixmap(str(Path(__file__).parent / 'assets' / icon)).scaled(26, 26, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter = QPainter(icon_pixmap)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(icon_pixmap.rect(), Qt.white)
            painter.end()
            mark.setPixmap(icon_pixmap)
            mark.setAlignment(Qt.AlignCenter)
            mark.setFixedSize(44, 44)
            mark.setStyleSheet(f'background: {color}; border: none; border-radius: 14px;')
            top.addWidget(mark)
            top.addSpacing(8)
            top.addWidget(value)
            top.addStretch()
            box.addLayout(top)
            caption_label = QLabel(caption)
            caption_label.setWordWrap(True)
            box.addWidget(caption_label)
            metrics.addWidget(card)
        root.addLayout(metrics)
        records = QFrame(objectName='historyRecords')
        records_box = QVBoxLayout(records)
        records_box.setContentsMargins(18, 16, 18, 16)
        records_box.setSpacing(12)
        records_box.addWidget(QLabel('Historial de informes', objectName='recordsTitle'))
        records_box.addWidget(QLabel('Consulta, filtra y gestiona tus informes académicos.', objectName='historyHint'))
        root.addWidget(records, 1)
        filters = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Buscar programa, periodo o archivo…')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.apply_filters)
        self.status = QComboBox()
        self.status.addItems(['Todos los estados', 'Terminados', 'Pendientes'])
        self.status.currentIndexChanged.connect(self.apply_filters)
        self.period = QComboBox()
        self.period.currentIndexChanged.connect(self.apply_filters)
        refresh = QPushButton('Actualizar')
        refresh.clicked.connect(self.refresh)
        filters.addWidget(self.search, 1)
        filters.addWidget(self.status)
        filters.addWidget(self.period)
        filters.addWidget(refresh)
        records_box.addLayout(filters)
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(['Programa', 'Periodo', 'Estado', 'Actualización', 'Archivo Excel', 'Acción'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.itemSelectionChanged.connect(self.update_action)
        self.table.itemDoubleClicked.connect(lambda _: self.activate())
        records_box.addWidget(self.table, 1)
        self.summary = QLabel(objectName='historyHint')
        records_box.addWidget(self.summary)
        actions = QHBoxLayout()
        browse = QPushButton('Buscar Excel guardados')
        browse.clicked.connect(self.browse_requested.emit)
        actions.addWidget(browse)
        actions.addStretch()
        self.action = QPushButton('Selecciona un proceso', objectName='historyPrimary')
        self.action.setEnabled(False)
        self.action.clicked.connect(self.activate)
        actions.addWidget(self.action)
        records_box.addLayout(actions)

    def refresh(self):
        try:
            records = list_completed_processes(self.user) + list_incomplete_processes(self.user)
        except Exception as error:
            show_error(self, 'No se pudo cargar el historial', str(error))
            return
        self.records = sorted(records, key=lambda r: str(r.get('updated_at') or ''), reverse=True)
        completed = sum(r['status'] == 'completed' for r in records)
        values = (len(records), completed, len(records)-completed, len({r['program'] for r in records if r.get('program')}))
        for label, value in zip(self.metrics, values):
            label.setText(str(value))
        previous = self.period.currentText()
        self.period.blockSignals(True)
        self.period.clear()
        self.period.addItem('Todos los periodos')
        self.period.addItems(sorted({str(r['period']) for r in records if r.get('period')}, reverse=True))
        self.period.setCurrentIndex(max(0, self.period.findText(previous)))
        self.period.blockSignals(False)
        self.apply_filters()

    def apply_filters(self, *_):
        for index, link in enumerate(self.side_links):
            link.setChecked(index == self.status.currentIndex())
        query = self.search.text().strip().casefold()
        rows = [r for r in self.records
                if (not query or query in ' '.join(str(r.get(k) or '') for k in ('program', 'period', 'workbook_path')).casefold())
                and (self.status.currentIndex() == 0 or (r['status'] == 'completed') == (self.status.currentIndex() == 1))
                and (self.period.currentIndex() <= 0 or str(r.get('period')) == self.period.currentText())]
        self.table.setRowCount(0)
        for index, record in enumerate(rows):
            self.table.insertRow(index)
            completed = record['status'] == 'completed'
            values = [record.get('program'), record.get('period'), 'Terminado' if completed else 'Pendiente', record.get('updated_at'), Path(record.get('workbook_path') or '').name]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value or '—'))
                item.setToolTip(str(value or ''))
                if column == 0:
                    item.setData(Qt.UserRole, record)
                    item.setIcon(QIcon(str(Path(__file__).parent / 'assets' / 'excel.svg')))
                if column == 2:
                    item.setForeground(QColor('#137346' if completed else '#946200'))
                    item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(index, column, item)
            status_cell = QWidget()
            status_layout = QHBoxLayout(status_cell)
            status_layout.setContentsMargins(4, 10, 4, 10)
            pill = QLabel('Terminado' if completed else 'Pendiente')
            pill.setMinimumHeight(26)
            pill.setAlignment(Qt.AlignCenter)
            pill.setStyleSheet('background: %s; color: %s; border-radius: 14px; font-size: 11px; padding: 5px;' % ('#EAF7F0' if completed else '#FFF6E5', '#137346' if completed else '#946200'))
            status_layout.addWidget(pill)
            status_cell.setAttribute(Qt.WA_TransparentForMouseEvents)
            self.table.setCellWidget(index, 2, status_cell)
            action_cell = QWidget()
            action_layout = QHBoxLayout(action_cell)
            action_layout.setContentsMargins(4, 8, 4, 8)
            open_action = QPushButton('Abrir' if completed else 'Retomar')
            open_action.setStyleSheet('padding: 7px 6px; font-size: 11px;')
            open_action.clicked.connect(lambda checked=False, row=index: self._activate_row(row))
            action_layout.addWidget(open_action)
            self.table.setCellWidget(index, 5, action_cell)
        self.summary.setText(f'{len(rows)} de {len(self.records)} procesos · El resumen superior muestra el total del historial.' if rows else 'No hay procesos que coincidan con los filtros.' if self.records else 'Todavía no hay procesos registrados. Empieza preparando un Excel desde Inicio.')
        self.update_action()

    def _activate_row(self, row):
        self.table.selectRow(row)
        self.activate()

    def selected(self):
        item = self.table.item(self.table.currentRow(), 0)
        return item.data(Qt.UserRole) if item else None

    def update_action(self):
        record = self.selected()
        self.action.setEnabled(bool(record))
        self.action.setText('Selecciona un proceso' if not record else 'Abrir Excel' if record['status'] == 'completed' else 'Continuar informe →')

    def activate(self):
        record = self.selected()
        if not record:
            return
        if record['status'] != 'completed':
            self.resume_requested.emit(record)
            return
        path = Path(record['workbook_path'])
        if not path.is_file():
            show_error(self, 'Archivo no encontrado', 'El archivo fue movido o eliminado. Puedes localizarlo con «Buscar Excel guardados».')
        elif not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.resolve()))):
            show_error(self, 'No se pudo abrir el archivo', 'Comprueba que tienes una aplicación para abrir archivos Excel.')
