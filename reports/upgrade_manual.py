from pathlib import Path
p=Path('reports/build_user_manual.py');s=p.read_text(encoding='utf-8');a=s.index('PAGES = [');b=s.index('\ndef build():',a);s=s[:a]+'from manual_content import PAGES\n'+s[b:]
s=s.replace('from PySide6.QtCore import QMarginsF','from PySide6.QtCore import QMarginsF, QUrl')
s=s.replace("        for heading, body in sections:\n            blocks.append", """        if index == 0:
            logo_url = QUrl.fromLocalFile(str(ASSETS / 'campus-virtual-logo.png')).toString()
            blocks.append(f'<p align="center"><img src="{logo_url}" width="260" height="75"></p>')
        for heading, body in sections:
            if heading == '@image':
                image_url = QUrl.fromLocalFile(str(BASE / 'reports' / body)).toString()
                blocks.append(f'<p align="center"><img src="{image_url}" width="530" height="331"></p>')
                continue
            blocks.append""")
p.write_text(s,encoding='utf-8')
