"""Lanza el build desde otra carpeta, con datos temporales y Qt sin pantalla."""
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

root = Path(__file__).resolve().parents[1]
if sys.platform == "darwin":
    executable = root / "dist/SantotoTunjaInformes.app/Contents/MacOS/SantotoTunjaInformes"
else:
    executable = root / "dist/SantotoTunjaInformes/SantotoTunjaInformes.exe"
with TemporaryDirectory(prefix="santoto_build_check_") as temporary:
    destination = Path(temporary)
    result = destination / "result.json"
    env = dict(os.environ, QT_QPA_PLATFORM="offscreen", SANTOTO_DATA_DIR=str(destination))
    subprocess.run([str(executable), "--smoke-test", str(result)], cwd=temporary, env=env, check=True, timeout=90)
    outcome = json.loads(result.read_text(encoding="utf-8"))
    assert outcome["ok"]
    assert Path(outcome["database"]).resolve() == (destination / "app.db").resolve()
print("Build verificado: Qt, imágenes, SVG, manual, plantilla, docx2pdf y SQLite.")
