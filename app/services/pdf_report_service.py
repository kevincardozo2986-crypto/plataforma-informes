"""Conversión del informe Word institucional a PDF en la misma carpeta.

Multiplataforma (sin licencia Microsoft por defecto):
- Prioridad a LibreOffice (gratis, `soffice --headless`).
- Word vía docx2pdf/COM solo como respaldo si LibreOffice no está instalado.
"""

import os
import platform
import shutil
import subprocess
import tempfile
import threading
import time
import unicodedata
from pathlib import Path


def _run_with_timeout(func, args, timeout, name):
    """Ejecuta un conversor con límite de tiempo en un hilo demonio.

    Si Word se bloquea con un diálogo abierto, la automatización se queda
    esperando para siempre y la interfaz no muestra ni error ni PDF.
    Con el timeout se libera la UI y se intenta el siguiente conversor.
    """
    outcome = {}

    def _target():
        try:
            outcome["value"] = func(*args)
        except BaseException as error:  # noqa: BLE001 - se re-lanza abajo
            outcome["error"] = error

    worker = threading.Thread(target=_target, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        raise TimeoutError(
            f"{name} tardó más de {timeout} segundos sin responder. "
            "Word quedó bloqueado (normalmente un diálogo abierto). "
            "Ciérralo e inténtalo de nuevo."
        )
    if "error" in outcome:
        raise outcome["error"]
    return outcome.get("value")


def _normalize_fs_path(path):
    """Normaliza una ruta para los conversores externos (Word/LibreOffice).

    En macOS el sistema de archivos guarda los tildes descompuestos (NFD)
    mientras Python suele usar compuestos (NFC); esa diferencia rompe la
    automatización de Word por AppleScript con "Mensaje incomprensible".
    Se prueba NFC primero y NFD como alternativa.
    """
    text = os.fspath(path)
    for form in ("NFC", "NFD"):
        candidate = Path(unicodedata.normalize(form, text))
        if candidate.exists():
            return candidate
    return Path(unicodedata.normalize("NFC", text))


def _convert_with_docx2pdf(word_path, pdf_path):
    from docx2pdf import convert

    word_path = _normalize_fs_path(word_path)
    if not word_path.is_file():
        raise FileNotFoundError(f"Word no encuentra el archivo: {word_path}")
    attempts = 2 if platform.system() == "Darwin" else 1
    last_error = None
    for attempt in range(attempts):
        try:
            _run_with_timeout(convert, (str(word_path), str(pdf_path)), 180, "docx2pdf")
            return
        except Exception as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(3)
    raise last_error


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
            _run_with_timeout(document.SaveAs, (str(pdf_path),), 180, "Word (COM)")
        finally:
            document.Close(False)
    finally:
        if word is not None:
            word.Quit()
        pythoncom.CoUninitialize()


def find_soffice():
    """Localiza el binario de LibreOffice aunque no esté en el PATH."""
    for name in ("soffice", "libreoffice"):
        found = shutil.which(name)
        if found:
            return found
    candidates = []
    system = platform.system()
    if system == "Darwin":
        candidates.append(Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"))
    elif system == "Windows":
        for base in (
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
            os.environ.get("ProgramW6432"),
        ):
            if base:
                candidates.append(Path(base) / "LibreOffice" / "program" / "soffice.exe")
    else:
        candidates.extend(
            [
                Path("/usr/bin/soffice"),
                Path("/usr/local/bin/soffice"),
                Path("/snap/bin/soffice"),
                Path("/opt/libreoffice/program/soffice"),
            ]
        )
        candidates.extend(Path("/opt").glob("libreoffice*/program/soffice"))
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


def _convert_with_libreoffice(word_path, pdf_path):
    soffice = find_soffice()
    if not soffice:
        raise FileNotFoundError(
            "LibreOffice (soffice) no está instalado ni en el PATH. "
            "Mac: brew install --cask libreoffice. "
            "Windows: instala desde libreoffice.org y agrega "
            "C:\\Program Files\\LibreOffice\\program al PATH."
        )
    word_path = _normalize_fs_path(word_path)
    if not word_path.is_file():
        raise FileNotFoundError(f"No se encuentra el Word: {word_path}")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    # Perfil aislado: evita bloqueos si LibreOffice ya está abierto
    # y fallos por perfil corrupto del usuario.
    with tempfile.TemporaryDirectory(prefix="soffice_profile_") as profile:
        try:
            completed = subprocess.run(
                [
                    soffice, "--headless", "--nolockcheck", "--nologo",
                    f"-env:UserInstallation=file:///{Path(profile).as_posix()}",
                    "--convert-to", "pdf",
                    "--outdir", str(pdf_path.parent), str(word_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired as error:
            raise TimeoutError(
                "LibreOffice tardó más de 180 segundos. "
                "Cierra LibreOffice e inténtalo de nuevo."
            ) from error
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[-800:]
        raise RuntimeError(f"LibreOffice falló ({completed.returncode}): {detail}")
    generated = pdf_path.parent / (word_path.stem + ".pdf")
    try:
        same_file = generated.resolve() == pdf_path.resolve()
    except OSError:
        same_file = False
    if not same_file:
        if generated.is_file():
            generated.replace(pdf_path)
    if not pdf_path.is_file():
        raise RuntimeError("LibreOffice terminó pero no generó el PDF.")


def convert_word_to_pdf(word_path, pdf_path=None, use_word_fallback=True):
    """Convierte un DOCX a PDF manteniendo el formato de la plantilla.

    Guarda el PDF en la misma carpeta del Word si no se indica otra ruta.
    Intenta en orden: LibreOffice (gratis, sin licencia Microsoft) y,
    solo si falla o no está instalado, Word vía docx2pdf/COM.

    En macOS esto además evita el crash silencioso de automatizar Word
    (AppleScript) desde un hilo secundario de Qt.
    """
    word_path = Path(word_path)
    if not word_path.is_file():
        raise FileNotFoundError("El documento Word no existe. Genera primero el Word.")
    if pdf_path is None:
        pdf_path = word_path.with_suffix(".pdf")
    else:
        pdf_path = Path(pdf_path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    converters = [("LibreOffice", _convert_with_libreoffice)]
    if use_word_fallback:
        converters.append(("docx2pdf (Word)", _convert_with_docx2pdf))
        if platform.system() == "Windows":
            converters.append(("Word (COM)", _convert_with_win32com))

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
        hint = (
            "Instala LibreOffice desde libreoffice.org y agrega "
            "C:\\Program Files\\LibreOffice\\program al PATH. "
            "Respaldo con Word: pip install docx2pdf pywin32"
        )
    elif platform.system() == "Darwin":
        hint = "Instala LibreOffice con: brew install --cask libreoffice"
    else:
        hint = "Instala LibreOffice (soffice) con tu gestor de paquetes"
    raise RuntimeError(
        "No fue posible convertir el Word a PDF. "
        f"{detail}. {hint}"
    )
