"""Conversión del informe Word institucional a PDF en la misma carpeta.

Multiplataforma:
- Windows: usa Word instalado vía docx2pdf o COM (pywin32), o LibreOffice.
- macOS: usa Word instalado vía docx2pdf, o LibreOffice (brew install --cask libreoffice).
"""

import platform
import shutil
import subprocess
from pathlib import Path


def _convert_with_docx2pdf(word_path, pdf_path):
    from docx2pdf import convert

    convert(str(word_path), str(pdf_path))


def _convert_with_win32com(word_path, pdf_path):
    if platform.system() != "Windows":
        raise RuntimeError("Word por COM solo está disponible en Windows.")
    import pythoncom
    from win32com import client

    pythoncom.CoInitialize()
    word = None
    try:
        word = client.DispatchEx("Word.Application")
        word.Visible = False
        word.DisplayAlerts = False
        document = word.Documents.Open(str(word_path), ReadOnly=True)
        try:
            # 17 = wdFormatPDF
            document.SaveAs(str(pdf_path), FileFormat=17)
        finally:
            document.Close(False)
    finally:
        if word is not None:
            word.Quit()
        pythoncom.CoUninitialize()


def _convert_with_libreoffice(word_path, pdf_path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise FileNotFoundError("LibreOffice (soffice) no está instalado.")
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf",
         "--outdir", str(pdf_path.parent), str(word_path)],
        check=True,
        capture_output=True,
        timeout=120,
    )
    generated = pdf_path.parent / (word_path.stem + ".pdf")
    try:
        same_file = generated.resolve() == pdf_path.resolve()
    except OSError:
        same_file = False
    if not same_file:
        if generated.is_file():
            generated.replace(pdf_path)


def convert_word_to_pdf(word_path, pdf_path=None):
    """Convierte un DOCX a PDF manteniendo el formato de la plantilla.

    Guarda el PDF en la misma carpeta del Word si no se indica otra ruta.
    Intenta en orden: docx2pdf (Word), Word por COM (solo Windows)
    y LibreOffice (Windows/macOS/Linux).
    """
    word_path = Path(word_path)
    if not word_path.is_file():
        raise FileNotFoundError("El documento Word no existe. Genera primero el Word.")
    if pdf_path is None:
        pdf_path = word_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    converters = [("docx2pdf (Word)", _convert_with_docx2pdf)]
    if platform.system() == "Windows":
        converters.append(("Word (COM)", _convert_with_win32com))
    converters.append(("LibreOffice", _convert_with_libreoffice))

    errors = []
    for name, converter in converters:
        try:
            converter(word_path.resolve(), pdf_path.resolve())
        except ImportError as error:
            errors.append(f"{name}: no disponible ({error})")
            continue
        except Exception as error:
            errors.append(f"{name}: {error}")
            continue
        if pdf_path.is_file():
            return pdf_path

    detail = "; ".join(errors) if errors else "sin conversor disponible"
    if platform.system() == "Windows":
        hint = "Instala Word o LibreOffice y ejecuta: pip install docx2pdf pywin32"
    elif platform.system() == "Darwin":
        hint = "Instala Word para Mac o ejecuta: brew install --cask libreoffice; pip install docx2pdf"
    else:
        hint = "Instala LibreOffice (soffice) y ejecuta: pip install docx2pdf"
    raise RuntimeError(
        "No fue posible convertir el Word a PDF. "
        f"{detail}. {hint}"
    )
