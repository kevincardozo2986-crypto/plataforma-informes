# Plataforma de Informes Santoto Tunja

Aplicación de escritorio para transformar archivos CSV exportados desde Moodle en informes Excel institucionales y, a partir del Excel terminado, generar el informe Word institucional con sus gráficos y su conversión a PDF. El proyecto permite administrar usuarios, configurar la información académica y ejecutar un flujo guiado de procesamiento sin depender de Microsoft Excel para el procesamiento.

## Tecnologías

- Python 3.10 o superior
- PySide6
- Pandas y NumPy
- OpenPyXL y XlsxWriter
- Matplotlib, Pillow
- python-docx, docx2pdf, pywin32 (solo Windows)
- SQLite
- Pytest

## Funcionalidades actuales

- Inicio de sesión con contraseñas protegidas mediante `scrypt` (`n=16384, r=8, p=1`).
- Roles de administrador y usuario.
- Administración de usuarios (crear, editar, activar/desactivar; el admin no puede eliminarse a sí mismo).
- Administración de periodos, niveles, modalidades y programas.
- Validación de periodos con formato `AAAA-S`, por ejemplo `2026-1`.
- Selección y validación de archivos CSV de Moodle.
- Detección automática de codificación (`utf-8-sig`, `utf-8`, `latin-1`) y separador (`,`, `;`, tabulación, `|`).
- Procesamiento de archivos grandes por bloques de 25.000 filas.
- Libro Excel de trabajo único y progresivo, con previsualización del mismo archivo que se está construyendo.
- Guardado automático del avance y recuperación de informes incompletos.
- Reintento de pasos fallidos sin cerrar la aplicación.
- Generación de informe Word institucional desde el Excel terminado, con tablas y gráficos Matplotlib.
- Conversión de Word a PDF en la misma carpeta (intenta primero LibreOffice y después las alternativas de Microsoft Word disponibles).
- Interfaz institucional con ventanas y diálogos personalizados.

## Hojas del libro Excel

El libro de trabajo (`SHEET_NAMES` en `app/services/excel_service.py`) contiene:

1. `Original`
2. `Tabla Dinamica Docentes`
3. `Docentes DG`
4. `Tabla Dinamica Estudiantes`
5. `Estudiantes DG`
6. `Estudiantes DG2`
7. `Tabla Dinamica Actividades`
8. `Resumen Informe`
9. `Diseño de Cursos`

Las hojas `DG` contienen los datos base para los gráficos. `Resumen Informe` concentra indicadores principales, actividad mensual, cursos destacados y continuidad docente para alimentar el Word.

## Tabla Dinamica Docentes

Filtra los registros cuyo rol sea:

```text
editingteacher
```

Para cada combinación de curso, docente y mes calcula la cantidad de días diferentes con actividad:

```python
nunique(Dia)
```

Los meses se generan dinámicamente con base en los datos disponibles. La columna `TOTAL` suma los valores mensuales de cada docente y al final se agrega una fila `PROMEDIO` con el promedio de cada mes.

## Informe Word institucional

El generador (`app/services/word_report_service.py:434`, `generate_word_report`) requiere un Excel terminado con estas hojas:

```text
Resumen Informe, Docentes DG, Tabla Dinamica Estudiantes, Diseño de Cursos
```

Lee los bloques `Indicadores principales`, `Actividad mensual`, `Cursos destacados` y `Continuidad docente`, genera gráficos de barras con Matplotlib y rellena la plantilla conservando sus estilos.

La plantilla forma parte del proyecto y debe conservarse en:

```text
templates/PLANTILLA_INFORME.docx
```

No es necesario seleccionarla manualmente: la aplicación la localiza automáticamente desde esa carpeta, incluso al ejecutarse como aplicación empaquetada.

La conversión a PDF guarda el PDF junto al Word. Requiere LibreOffice o Microsoft Word instalado en el equipo de destino; instalar las librerías Python no instala estas aplicaciones.

## Requisitos del CSV

El archivo debe tener extensión `.csv`. Para la validación inicial solo se exige:

```text
FechaUnix
```

Para el procesamiento completo se usan además:

```text
curso, usuario, rol
```

Los nombres se comparan sin distinguir mayúsculas y minúsculas y sin espacios sobrantes. A partir de `FechaUnix`, la aplicación genera:

```text
Fecha, Mes, Dia
```

## Instalación

### Descargar la aplicación

Las versiones compiladas están en [GitHub Releases](https://github.com/kevincardozo2986-crypto/plataforma-informes/releases/latest).

- **Windows:** descarga `SantotoTunjaInformes-Windows.zip`, extrae toda la carpeta y abre `SantotoTunjaInformes.exe`.
- **Mac con chips M:** descarga `SantotoTunjaInformes-macOS-AppleSilicon.zip` y extrae la aplicación `.app`.
- **Mac con Intel:** descarga `SantotoTunjaInformes-macOS-Intel.zip` y extrae la aplicación `.app`.

### Ejecutar desde el código fuente

Clona el repositorio y entra en la carpeta del proyecto:

```bash
git clone https://github.com/kevincardozo2986-crypto/plataforma-informes.git
cd plataforma-informes
git switch develop
```

Crea un entorno virtual:

```bash
python -m venv venv
```

Actívalo en Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

En Linux o macOS:

```bash
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

```bash
python main.py
```

La aplicación incluye un acceso fijo de respaldo: usuario `admin`, contraseña `admin`. La cuenta se crea automáticamente si falta, incluso cuando ya existen otros usuarios. Entrar con estas credenciales recupera el rol de administrador y activa la cuenta, conservando su identificador, sus informes y su contraseña personalizada si ya existía. Este acceso sigue funcionando aunque se cambie la contraseña o se desactive la cuenta; cualquier persona que conozca estas credenciales puede entrar como administrador. Las variables `SANTOTO_ADMIN_USERNAME` y `SANTOTO_ADMIN_PASSWORD` ya no se utilizan.

## Flujo de uso

### Excel

1. Inicia sesión.
2. Abre el módulo de generación de Excel.
3. Selecciona periodo, nivel académico, modalidad y programa.
4. Selecciona la carpeta institucional de destino.
5. Selecciona el CSV exportado desde Moodle.
6. Pulsa `Cargar CSV`.
7. Ejecuta los pasos en orden (`Crear hoja Original`, `Convertir FechaUnix`, `Procesar docentes`, estudiantes, actividades, resumen y diseño).
8. Previsualiza y guarda el Excel resultante.

El diagrama de diseño de cursos clasifica como «Con contenido» los cursos con al menos una acción `create` o `created` en la tabla dinámica de actividades (CRUD). Las visitas, actualizaciones y eliminaciones no cuentan como creación. Los cursos sin creaciones quedan «Sin contenido» y los unificados mantienen su categoría aparte.

La carga del CSV filtra por el período seleccionado usando la fecha local de Colombia: `AAAA-1` abarca enero–junio y `AAAA-2` julio–diciembre. Al terminar informa los registros excluidos por período o fecha inválida y los registros sin identificador de usuario. Si no hay registros válidos del período, muestra un error y conserva el Excel anterior.

El total de estudiantes por curso cuenta identificadores distintos durante todo el período, sin sumar repetidamente a quienes participaron en varios meses. Los docentes se agrupan por curso e `idusuario`, conservando su nombre para mostrarlo; los archivos antiguos sin columna `idusuario` mantienen la agrupación por nombre. Los registros sin ID no se cuentan como personas, aunque sus acciones se conservan en el CRUD. Para aplicar estas correcciones a informes anteriores, vuelve a procesar el CSV y genera nuevamente Excel y Word/PDF.

Los administradores y usuarios normales pueden consultar, agregar, editar y eliminar períodos, niveles académicos, modalidades y programas/carreras mediante el botón `+` de cada lista del carpeteo. Debe quedar al menos una opción en cada lista. Los cursos del informe se obtienen del CSV de Moodle.

### Word / PDF

1. Abre el módulo de informe Word.
2. Selecciona el Excel terminado del paso anterior.
3. Genera el Word (la plantilla se aplica sola).
4. Convierte a PDF desde la misma ventana si lo necesitas.

## Pruebas

Ejecuta la suite con:

```bash
python -m pytest -q
```

La suite actual contiene 46 pruebas automatizadas en 7 archivos (`tests/test_*.py`): autenticación, usuarios, opciones académicas, rutas institucionales, historial de procesos, servicios Excel y generación Word.

## Datos locales

La base SQLite y los CSV reales están excluidos mediante `.gitignore`. Hay documentos de trabajo ya versionados; las reglas de exclusión no los retiran del historial. El empaquetado incluye solo los recursos de ejecución y deja fuera esos documentos y los datos locales.

Rutas locales principales:

```text
data/app.db
data/*.csv
data/*.xlsx
reports/*.xlsx
reports/*.docx
reports/*.pdf
debug_output/
debug_output2/
*.db
```

## Estructura del proyecto

```text
app/
├── database/    # Conexión e inicialización de SQLite
├── models/      # Conversión de entidades
├── services/    # auth, csv, excel, chart, word, pdf, historial, opciones y rutas
└── ui/          # login, dashboard, proceso Excel, informe Word, usuarios, temas
templates/        # PLANTILLA_INFORME.docx institucional
tests/            # Pruebas automatizadas
data/             # Base local y CSV reales (no versionado)
reports/          # Informes generados (no versionado)
main.py           # Punto de entrada
```

## Estado del proyecto

Proyecto académico en desarrollo para la automatización de informes de uso de Moodle de la Universidad Santo Tomás. Genera el libro Excel completo, el Word institucional y su PDF.

## Empaquetado para Windows y macOS

El workflow **Build** (`.github/workflows/build.yml`) se ejecuta manualmente desde **Actions → Build → Run workflow**. Compila el mismo código con `build.spec` en runners independientes de Windows y macOS y entrega los artifacts `SantotoTunjaInformes-Windows` y `SantotoTunjaInformes-macOS-Intel` y `SantotoTunjaInformes-macOS-AppleSilicon`.

Consulta [Distribución y requisitos del equipo de destino](docs/DISTRIBUCION.md) para el primer inicio, ubicación de SQLite, builds locales, limitaciones de firma y requisitos de conversión a PDF. El workflow debe estar en la rama predeterminada de GitHub para aparecer en la interfaz de ejecución manual.

Para un iMac con procesador Intel, descarga **SantotoTunjaInformes-macOS-Intel**. Para equipos con chips M1, M2, M3 u otros Apple Silicon, descarga **SantotoTunjaInformes-macOS-AppleSilicon**. Son builds nativos separados, no una aplicación universal.
