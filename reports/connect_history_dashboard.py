from pathlib import Path
p=Path('app/ui/dashboard_window.py');s=p.read_text(encoding='utf-8')
s=s.replace('from app.ui.users_window import UsersPage','from app.ui.users_window import UsersPage\nfrom app.ui.history_page import HistoryPage')
s=s.replace('        self.stack.addWidget(self.word_page)','''        self.stack.addWidget(self.word_page)
        self.history_page = HistoryPage(user)
        self.history_page.back_requested.connect(self._show_dashboard)
        self.history_page.resume_requested.connect(self._resume_history_process)
        self.history_page.browse_requested.connect(self._open_saved_history)
        self.stack.addWidget(self.history_page)''',1)
a=s.index('    def _open_history(self):');b=s.index('    def _open_saved_history(self):',a)
s=s[:a]+'''    def _open_history(self):
        self.history_page.refresh()
        self.stack.setCurrentWidget(self.history_page)

    def _resume_history_process(self, process):
        if self.excel_page.resume_process(process):
            self.stack.setCurrentWidget(self.excel_page)

'''+s[b:]
p.write_text(s,encoding='utf-8')
