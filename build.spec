"""Build nativo: python -m PyInstaller --noconfirm --clean build.spec."""
from pathlib import Path
import sys
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

ROOT = Path(SPECPATH)
NAME = "SantotoTunjaInformes"
# Solo recursos de ejecución: nunca data/, reports/, .env ni el repositorio entero.
datas = [
    (str(path), str(path.parent.relative_to(ROOT)))
    for path in sorted((ROOT / "app" / "ui" / "assets").rglob("*"))
    if path.is_file() and path.suffix.lower() in {".png", ".svg", ".ico", ".icns", ".pdf"}
]
datas.append((str(ROOT / "templates" / "PLANTILLA_INFORME.docx"), "templates"))
# docx2pdf consulta su versión y ejecuta convert.jxa mediante osascript en macOS.
datas += copy_metadata("docx2pdf")
datas += collect_data_files("docx2pdf", includes=["*.jxa"])

a = Analysis(
    [str(ROOT / "main.py")], pathex=[str(ROOT)], datas=datas,
    binaries=[], hiddenimports=[], hookspath=[], runtime_hooks=[],
    excludes=["pytest", "tkinter"],
    hooksconfig={"matplotlib": {"backends": ["Agg"]}},
)
pyz = PYZ(a.pure)
icon_path = ROOT / "app" / "ui" / "assets" / ("app.icns" if sys.platform == "darwin" else "app.ico")
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name=NAME,
    debug=False, strip=False, upx=False, console=False,
    icon=str(icon_path) if icon_path.is_file() else None,
    codesign_identity=None, entitlements_file=None,
)
collection = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=NAME)
if sys.platform == "darwin":
    app = BUNDLE(
        collection, name=NAME + ".app",
        icon=str(icon_path) if icon_path.is_file() else None,
        bundle_identifier="co.santototunja.informes",
        info_plist={"CFBundleDisplayName": "Plataforma de Informes Santoto Tunja",
                   "NSHighResolutionCapable": True,
                   "NSAppleEventsUsageDescription": "Convierte informes Word a PDF cuando se utiliza Microsoft Word."},
    )
