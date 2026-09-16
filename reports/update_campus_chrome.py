from pathlib import Path
p=Path('app/ui/window_chrome.py'); s=p.read_text(encoding='utf-8')
s=s.replace('background: qlineargradient(x1:0, y1:0, x2:1, y2:0,\n        stop:0 #05294F, stop:0.55 #073B6E, stop:1 #0A4A84);\n    border: none; border-bottom: 2px solid #2C6DA5;', 'background: #FFFFFF;\n    border: none; border-bottom: 1px solid #DCE5EF;')
s=s.replace('background-color: #124D7F; color: #FFFFFF;\n    border: none; border-left: 1px solid #2A628F;', 'background-color: #FFFFFF; color: #173653;\n    border: none; border-left: 1px solid #EDF1F6;')
s=s.replace('QPushButton#mainWindowControl:hover { background-color: #24699F; color: #FFFFFF; }','QPushButton#mainWindowControl:hover { background-color: #EDF4FB; color: #173653; }')
s=s.replace('altura = 44 if controles_completos else 40','altura = 68 if controles_completos else 40')
a=s.index('        if controles_completos:\n            marca = QLabel()')
b=s.index('        else:\n',a)
s=s[:a]+'''        if controles_completos:
            marca = QLabel()
            marca.setObjectName("campusBrandLogo")
            marca.setPixmap(QPixmap(str(Path(__file__).parent / "assets" / "campus-virtual-logo.png")).scaled(210, 61, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            marca.setFixedSize(224, 66)
            marca.setAlignment(Qt.AlignCenter)
            marca.setAccessibleName("Campus Virtual")
            marca.setAttribute(Qt.WA_TransparentForMouseEvents)
            diseno.addWidget(marca)
'''+s[b:]
p.write_text(s,encoding='utf-8')
