# Plataforma de Informes USTA

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
- Conversión de Word a PDF en la misma carpeta (intenta `docx2pdf`, Word por COM y LibreOffice, en ese orden).
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

La conversión a PDF (`app/services/pdf_report_service.py:52`, `convert_word_to_pdf`) guarda el PDF junto al Word. En Windows requiere Word instalado o `pip install docx2pdf pywin32`; en Linux/macOS requiere LibreOffice (`soffice`).

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

En la primera ejecución se crea automáticamente la base de datos local y un administrador inicial:

```text
Usuario: admin
Contraseña: Admin123
```

Se recomienda cambiar esta contraseña desde la administración de usuarios antes de utilizar la aplicación con información real.

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

El administrador puede agregar, editar o eliminar las opciones académicas. Los usuarios normales solo pueden seleccionarlas.

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

La base SQLite, los CSV reales, los informes generados y las carpetas de depuración no se suben al repositorio. Están excluidos mediante `.gitignore` para evitar publicar datos institucionales o personales.

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
