# Distribución para Windows y macOS

## Análisis del proyecto

El punto de entrada es `main.py`: su bloque `__main__` llama a `main()`, que crea `QApplication`, configura la paleta, inicializa SQLite y muestra `LoginWindow`. Tras autenticar, abre `DashboardWindow`. Es una aplicación de escritorio PySide6, no un servidor ni una aplicación de consola.

Las dependencias están en `requirements.txt`; no hay otro sistema de paquetes. Los imports utilizan PySide6, pandas, NumPy (también utilizado por las dependencias), openpyxl, xlsxwriter, matplotlib con backend Agg, Pillow, python-docx y docx2pdf. `pythoncom` y `win32com` corresponden a `pywin32`, que ya tiene un marcador exclusivo para Windows. Pytest se utiliza para verificar el proyecto. No se cambian estas dependencias; PyInstaller se instala como herramienta de compilación.

Recursos incluidos:

- Imágenes, SVG y manual PDF de `app/ui/assets/`, conservando sus rutas.
- `templates/PLANTILLA_INFORME.docx`, utilizado por el servicio de Word.
- Los metadatos de docx2pdf y su script `convert.jxa`, necesario para automatizar Word en macOS.
- Los recursos y librerías de las dependencias recogidos por los hooks de PyInstaller, incluidos Qt y Matplotlib.

El CSS de Qt está en módulos Python. El HTML de `reports/manual_usuario.html` es una fuente de documentación; la aplicación entrega el PDF y no necesita ese HTML. `resources/` está vacío. `app/models/` contiene código Python, no modelos externos. No existen recursos de frontend web que deban incorporarse. Los scripts de generación de manuales en `reports/` son herramientas de desarrollo; no se ejecutan ni se incluyen en la aplicación distribuida.

Las rutas basadas en `__file__` y la búsqueda de plantilla mediante `_MEIPASS` ya permiten empaquetar. Se mantienen. La única ruta de datos que necesitaba adaptación era SQLite, que debe escribirse fuera del paquete instalado.

## Generar desde GitHub

1. Sube los cambios, incluido `build.spec`, `.github/workflows/build.yml`, los nuevos iconos y `scripts/check_bundle.py`.
2. El workflow debe estar presente en la rama predeterminada para aparecer en la interfaz de ejecución manual de GitHub. Si trabajas en `develop`, intégralo también en la rama predeterminada cuando corresponda.
3. Abre **Actions → Build → Run workflow** y selecciona la rama a compilar.
4. Al terminar los tres trabajos, descarga los artifacts de esa ejecución:
   - `SantotoTunjaInformes-Windows`: contiene `SantotoTunjaInformes-Windows.zip`.
   - `SantotoTunjaInformes-macOS-Intel` y `SantotoTunjaInformes-macOS-AppleSilicon`: contiene el ZIP de la arquitectura elegida.

El workflow solo se activa manualmente. Los tres jobs hacen checkout de la misma revisión, usan Python 3.13 y PyInstaller 6.22.3, instalan las dependencias, ejecutan las pruebas, compilan y verifican el paquete. Windows se compila en `windows-latest` y macOS Apple Silicon en `macos-latest` y macOS Intel en `macos-15-intel`. No hay compilación cruzada. Los artifacts se conservan 14 días; descarga y guarda las entregas que necesites conservar.

## Qué recibe el usuario

En Windows, extrae el ZIP y conserva **toda** la carpeta `SantotoTunjaInformes`, incluido `_internal`. Abre `SantotoTunjaInformes.exe`. Es una distribución portable de carpeta, no un instalador ni un ejecutable autónomo que pueda moverse separado de sus librerías.

En macOS, extrae el ZIP y copia `SantotoTunjaInformes.app` a Aplicaciones o a una carpeta propia. El ZIP se genera con `ditto` para conservar la estructura del bundle y los enlaces. No necesita tener Python instalado.

La arquitectura corresponde a Python y al runner nativo utilizado. El workflow no promete un binario universal de macOS ni compatibilidad con todas las versiones antiguas del sistema. Consulta la arquitectura y versión del runner en los logs; para equipos de otra arquitectura se necesita un build nativo adicional. Los alias `*-latest` pueden cambiar de imagen con el tiempo.

No se configura firma de editor para Windows, certificado Developer ID ni notarización de Apple. Windows puede mostrar SmartScreen y macOS puede bloquear inicialmente la aplicación descargada. PyInstaller puede aplicar la firma ad hoc necesaria para ejecutar en Apple Silicon; eso no equivale a firma de distribución ni notarización. No se incluye un icono de ejecutable personalizado porque los recursos actuales no contienen `.ico`/`.icns`; los iconos de la interfaz siguen incluidos.

## Datos y primera ejecución

El ejecutable no contiene la base de datos de desarrollo, usuarios, informes, CSV, bitácoras ni archivos `.env`. Tampoco necesita secretos de GitHub para compilar. Sí incluye las credenciales fijas de respaldo descritas a continuación.

El acceso de respaldo es `admin` / `admin`. Al iniciar se crea la cuenta si falta, aunque existan otros usuarios. Iniciar sesión con estas credenciales reactiva la cuenta y recupera el rol de administrador, conservando su identificador y contraseña personalizada. Cambiar la contraseña o desactivar la cuenta no deshabilita el acceso fijo. Las variables `SANTOTO_ADMIN_USERNAME` y `SANTOTO_ADMIN_PASSWORD` ya no se utilizan.

SQLite se crea en:

- Windows: `%LOCALAPPDATA%\SantotoTunjaInformes\app.db`.
- macOS: `~/Library/Application Support/SantotoTunjaInformes/app.db`.
- Desde código fuente: `data/app.db`, como antes.

`SANTOTO_DATA_DIR` permite elegir otra carpeta de datos escribible. Las bases existentes no se copian automáticamente a las instalaciones nuevas. Cada instalación conserva sus cuentas e historial fuera del ejecutable, incluso al reemplazar el paquete por una actualización. Los informes siguen guardándose donde el usuario elige en la interfaz.

Hay documentos de trabajo y bitácoras ya versionados en el repositorio. El `.spec` los excluye explícitamente por selección de recursos; esto no los elimina del repositorio ni de su historial. Revisa su contenido antes de hacer público el repositorio.

## Conversión a PDF

LibreOffice o Microsoft Word deben estar instalados en el equipo de destino; PyInstaller no los incluye. El servicio intenta primero LibreOffice y después las alternativas de Word disponibles. Instalar docx2pdf o pywin32 no instala Microsoft Word ni proporciona su licencia. macOS puede solicitar permiso para automatizar Word. La generación de Excel y Word no necesita esas aplicaciones externas.

## Build y verificación local

Desde un entorno virtual del sistema de destino:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller==6.22.3
python -m pytest tests -q
python -m PyInstaller --noconfirm --clean build.spec
python scripts/check_bundle.py
```

`check_bundle.py` ejecuta el binario desde una carpeta temporal con Qt fuera de pantalla. Comprueba imports, apertura del login, imagen PNG, SVG, manual PDF, plantilla DOCX, script de docx2pdf y creación de SQLite en una carpeta temporal. No autentica con cuentas reales ni convierte con Office; la conversión efectiva a PDF y la apariencia final deben revisarse también en los equipos de entrega.

Referencias: [specs de PyInstaller](https://pyinstaller.org/en/stable/spec-files.html), [rutas en ejecución](https://pyinstaller.org/en/stable/runtime-information.html), [workflows manuales de GitHub](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

Para un iMac con procesador Intel, descarga **SantotoTunjaInformes-macOS-Intel**. Para equipos con chips M1, M2, M3 u otros Apple Silicon, descarga **SantotoTunjaInformes-macOS-AppleSilicon**. Son builds nativos separados, no una aplicación universal.
