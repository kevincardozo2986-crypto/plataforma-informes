from pathlib import Path
from copy import deepcopy
from datetime import date, timedelta
import zipfile
import xml.etree.ElementTree as ET

SOURCE = Path(r'C:\Users\kevin\Desktop\OctavoSemestre\PRACTICAS\Evidencias de Practicas\Bitacora_semanal_practica_empresarial.docx')
OUT = Path(__file__).parent / 'bitacoras_agosto_septiembre'
OUT.mkdir(exist_ok=True)
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
NS = {'w': W[1:-1]}
activities = {
    '2026-08-19': ('AnÃ¡lisis inicial y estructura del proyecto', 'RevisiÃ³n del flujo de la aplicaciÃ³n y de las necesidades solicitadas. CreaciÃ³n de la estructura de carpetas del proyecto.'),
    '2026-08-20': ('Inicio de sesiÃ³n y gestiÃ³n de usuarios', 'ImplementaciÃ³n del inicio de sesiÃ³n y de las operaciones de creaciÃ³n, consulta, actualizaciÃ³n y eliminaciÃ³n de usuarios. Avance en el panel principal.'),
    '2026-08-21': ('Panel principal y archivo Excel', 'Avance en el panel principal y en la organizaciÃ³n de carpetas. Inicio de la creaciÃ³n del archivo Excel y de su primera hoja.'),
    '2026-08-24': ('Opciones de administraciÃ³n', 'IncorporaciÃ³n de botones para que el administrador cree opciones de configuraciÃ³n, como pregrado y nivel.'),
}

def put(cell, text):
    p = cell.find('w:p', NS)
    if p is None:
        p = ET.SubElement(cell, W + 'p')
    for child in list(cell):
        if child.tag != W + 'tcPr' and child is not p:
            cell.remove(child)
    for child in list(p):
        if child.tag != W + 'pPr':
            p.remove(child)
    run = ET.SubElement(p, W + 'r')
    props = ET.SubElement(run, W + 'rPr')
    ET.SubElement(props, W + 'sz', {W + 'val': '20'})
    ET.SubElement(run, W + 't').text = text

with zipfile.ZipFile(SOURCE) as archive:
    xml = archive.read('word/document.xml')
    for _, pair in ET.iterparse(__import__('io').BytesIO(xml), events=['start-ns']):
        if not pair[0].startswith('ns'):
            ET.register_namespace(*pair)
    for week, (start, end) in enumerate([(date(2026,8,19),date(2026,8,21)), (date(2026,8,24),date(2026,8,28)), (date(2026,8,31),date(2026,9,4)), (date(2026,9,7),date(2026,9,7))], 1):
        root = ET.fromstring(xml)
        for element in root.iter():
            for attr in list(element.attrib):
                if attr.startswith('{http://schemas.openxmlformats.org/markup-compatibility/2006}'):
                    del element.attrib[attr]
        tables = root.findall('w:body/w:tbl', NS)
        rows = tables[0].findall('w:tr', NS)
        put(rows[0].findall('w:tc',NS)[1], 'Kevin Esteban Cardozo Cepeda')
        put(rows[3].findall('w:tc',NS)[1], str(week))
        put(rows[3].findall('w:tc',NS)[3], f'Del {start:%d/%m/%Y} al {end:%d/%m/%Y}')
        table = tables[1]
        template = deepcopy(table.findall('w:tr',NS)[1])
        for row in table.findall('w:tr',NS)[1:]:
            table.remove(row)
        total = 0
        day = start
        while day <= end:
            hours = [2,5,3,4,5][day.weekday()]
            total += hours
            row = deepcopy(template)
            title, detail = activities.get(day.isoformat(), ('', ''))
            for cell, value in zip(row.findall('w:tc',NS), [f'{day:%d/%m/%Y}', title, detail, str(hours)]):
                put(cell, value)
            table.append(row)
            day += timedelta(days=1)
        put(tables[2].findall('w:tr',NS)[0].findall('w:tc',NS)[1], str(total))
        target = OUT / f'Borrador_semana_{week}_{start:%d-%m}_{end:%d-%m}.docx'
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as dest:
            for item in archive.infolist():
                dest.writestr(deepcopy(item), ET.tostring(root, encoding='utf-8', xml_declaration=True) if item.filename == 'word/document.xml' else archive.read(item.filename))
        print(f'{target}: {total} horas')

