# Plataforma de Informes USTA

Aplicación de escritorio para transformar archivos CSV exportados desde Moodle en informes Excel institucionales. El proyecto permite administrar usuarios, configurar la información académica y ejecutar un flujo guiado de procesamiento sin depender de Microsoft Excel.

## Tecnologías

- Python 3.10 o superior
- PySide6
- Pandas y NumPy
- OpenPyXL
- XlsxWriter
- SQLite
- Pytest

## Funcionalidades actuales

- Inicio de sesión con contraseñas protegidas mediante `scrypt`.
- Roles de administrador y usuario.
- Administración de usuarios.
- Administración de periodos, niveles, modalidades y programas.
- Validación de periodos con formato `AAAA-S`, por ejemplo `2026-1`.
- Selección y validación de archivos CSV de Moodle.
- Detección automática de codificación y separador del CSV.
- Procesamiento de archivos grandes por bloques.
- Generación y previsualización del mismo libro Excel de trabajo.
- Guardado automático del avance y recuperación de informes incompletos.
- Reintento de pasos fallidos sin cerrar la aplicación.
- Interfaz institucional con ventanas y diálogos personalizados.

Actualmente se generan exclusivamente estas hojas:

1. `Original`
2. `Tabla Dinamica Docentes`

Las demás hojas del informe todavía no están implementadas.

## Tabla Dinamica Docentes

La segunda hoja filtra los registros cuyo rol sea:

```text
editingteacher
```

Para cada combinación de curso, docente y mes calcula la cantidad de días diferentes con actividad:

```python
nunique(Dia)
```

Los meses se generan dinámicamente con base en los datos disponibles. La columna `TOTAL` suma los valores mensuales de cada docente y al final se agrega una fila `PROMEDIO` con el promedio de cada mes.

## Requisitos del CSV

El archivo debe tener extensión `.csv` e incluir, como mínimo, las columnas utilizadas por el procesamiento:

```text
curso
usuario
rol
FechaUnix
```

Los nombres se comparan sin distinguir mayúsculas y minúsculas. A partir de `FechaUnix`, la aplicación genera:

```text
Fecha
Mes
Dia
```

Se admiten normalmente archivos separados por coma, punto y coma, tabulación o `|`, con codificación UTF-8 o Latin-1.

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

La plantilla institucional usada para crear los documentos Word forma parte del
proyecto y debe conservarse en esta ruta al copiarlo o clonarlo:

```text
templates/PLANTILLA_INFORME.docx
```

No es necesario seleccionarla manualmente: la aplicación la localiza desde esa
carpeta, independientemente del directorio desde el cual se ejecute.

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

1. Inicia sesión.
2. Abre el módulo de generación de Excel.
3. Selecciona periodo, nivel académico, modalidad y programa.
4. Selecciona la carpeta institucional de destino.
5. Selecciona el CSV exportado desde Moodle.
6. Pulsa `Cargar CSV`.
7. Ejecuta `Crear hoja Original`.
8. Ejecuta `Convertir FechaUnix`.
9. Ejecuta `Procesar docentes`.
10. Previsualiza y guarda el Excel resultante.

El administrador puede agregar, editar o eliminar las opciones académicas. Los usuarios normales solo pueden seleccionarlas.

## Pruebas

Ejecuta la suite con:

```bash
python -m pytest -q
```

La suite actual contiene 39 pruebas automatizadas.

## Datos locales

La base SQLite, los CSV reales y los informes generados no se suben al repositorio. Están excluidos mediante `.gitignore` para evitar publicar datos institucionales o personales.

Rutas locales principales:

```text
data/app.db
data/*.csv
reports/*.xlsx
```

## Estructura del proyecto

```text
app/
├── database/    # Conexión e inicialización de SQLite
├── models/      # Conversión de entidades
├── services/    # Autenticación y procesamiento CSV/Excel
└── ui/          # Ventanas, diálogos, temas y recursos visuales
tests/            # Pruebas automatizadas
main.py           # Punto de entrada
```

## Estado del proyecto

Proyecto académico en desarrollo para la automatización de informes de uso de Moodle de la Universidad Santo Tomás.
