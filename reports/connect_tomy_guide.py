from pathlib import Path
p=Path('app/ui/dashboard_window.py')
s=p.read_text(encoding='utf-8').replace('from app.ui.assistant import anchor_bottom_right','from app.ui.assistant import anchor_bottom_right, MascotButton, show_assistant')
s=s.replace('title_row.addWidget(count)', 'title_row.addWidget(count)\n        title_row.addWidget(MascotButton("historial", dialog))')
a=s.index('    def _open_saved_history(')
b=s.index('    def _choose_base_directory',a)
part=s[a:b]
part=part.replace('content.addWidget(title)', 'title_row = QHBoxLayout()\n        title_row.addWidget(title, 1)\n        title_row.addWidget(MascotButton("historial", dialog))\n        content.addLayout(title_row)',1)
idx=part.index('    def _open_configuration')
part=part[:idx]+part[idx:].replace('content.addWidget(title)', 'title_row = QHBoxLayout()\n        title_row.addWidget(title, 1)\n        title_row.addWidget(MascotButton("configuracion", dialog))\n        content.addLayout(title_row)',1)
s=s[:a]+part+s[b:]
a=s.index('    def _open_help(self):')
# Preserve following methods.
b=s.find('\n    def ',a+5)
if b<0: b=len(s)
s=s[:a]+'    def _open_help(self):\n        show_assistant(self, "inicio")\n'+s[b:]
p.write_text(s,encoding='utf-8')
