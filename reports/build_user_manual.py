"""Genera el manual distribuido con la aplicación usando Qt, sin servicios externos."""
from pathlib import Path
from html import escape
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextDocument, QPdfWriter, QPageSize, QPageLayout, QFontDatabase
from PySide6.QtCore import QMarginsF, QUrl

BASE = Path(__file__).resolve().parents[1]
ASSETS = BASE / 'app/ui/assets'
from manual_content import PAGES

def build():
    app = QApplication.instance() or QApplication([])
    for font in ('segoeui.ttf', 'segoeuib.ttf'):
        QFontDatabase.addApplicationFont('C:/Windows/Fonts/' + font)
    blocks = []
    for index, (title, subtitle, sections) in enumerate(PAGES):
        blocks.append('<div style="%s">' % ('page-break-before:always;' if index else ''))
        blocks.append('<table width="100%%" bgcolor="#103D6C" cellpadding="18"><tr><td><font color="#F3CA65">GUÍA DE USO · Santoto Tunja</font><h1 style="color:white">%s</h1><p style="color:#DBEAFA">%s</p></td></tr></table>' % (escape(title), escape(subtitle)))
        if index == 0:
            logo_url = QUrl.fromLocalFile(str(ASSETS / 'campus-virtual-logo.png')).toString()
            blocks.append(f'<p align="center"><img src="{logo_url}" width="260" height="75"></p>')
        for heading, body in sections:
            if heading == '@image':
                image_url = QUrl.fromLocalFile(str(BASE / 'reports' / body)).toString()
                blocks.append(f'<p align="center"><img src="{image_url}" width="530" height="331"></p>')
                continue
            blocks.append('<h3>%s</h3><p>%s</p>' % (escape(heading), escape(body).replace('\n', '<br>')))
        blocks.append('<p style="color:#718096;font-size:9pt">Plataforma de Informes Santoto Tunja · Manual de usuario · %s / %s</p></div>' % (index+1, len(PAGES)))
    html = '<html><head><meta charset="utf-8"><style>body{font-family:"Segoe UI";font-size:10pt;color:#243B53} h1{font-size:24pt} h3{color:#0B5DAC;font-size:12pt;margin-top:15px;margin-bottom:5px} p{margin-top:4px;margin-bottom:8px}</style></head><body>' + ''.join(blocks) + '</body></html>'
    (BASE / 'reports/manual_usuario.html').write_text(html, encoding='utf-8')
    doc = QTextDocument()
    doc.setHtml(html)
    writer = QPdfWriter(str(ASSETS / 'manual-usuario.pdf'))
    writer.setTitle('Manual de usuario · Plataforma de Informes Santoto Tunja')
    writer.setCreator('Plataforma de Informes Santoto Tunja')
    writer.setPageSize(QPageSize(QPageSize.A4))
    writer.setPageMargins(QMarginsF(16, 14, 16, 14), QPageLayout.Millimeter)
    doc.print_(writer)
    print(ASSETS / 'manual-usuario.pdf')

if __name__ == '__main__':
    build()
