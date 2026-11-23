# Carpeta de apoyo / Scripts de comprobación manual

Los archivos contenidos en esta carpeta son usados para ver que las files principales funcionan correctamente.

Esta carpeta contiene scripts auxiliares utilizados durante el desarrollo para comprobar el funcionamiento de distintos módulos del proyecto.

Estos scripts permiten realizar comprobaciones manuales y no sustituyen a los tests automatizados de la carpeta `tests/`.

## `check_loader.py`
Comprueba que los archivos CSV originales se cargan correctamente mediante la función `load_data()` del módulo `book_recommender.loader`.

Requiere disponer de los archivos originales en `data/raw/`.

## `check_recommender.py`
Permite comprobar los tres modos de recomendación utilizando un modelo ya entrenado.

Antes de ejecutarlo, es necesario generar un modelo mediante el pipeline. Por ejemplo:

`python -m book_recommender.cli --model-output artifacts/book_recommender_tags_test.joblib`

La ruta del modelo debe coincidir con la indicada en la variable model_path del script.

## `inspect_tags.py`
Permite inspeccionar las etiquetas del dataset y analizar su clasificación temática.

El archivo `inspect_tags.py` se ha usado para ver que tags son los mas usados y las categorias mas frecuentes presentes en `tags.csv` teniendo en cuenta a que libro/s pertenece definido en `book_tags.csv`.

Se ha utilizado durante el desarrollo para revisar y ajustar las constantes del módulo `book_recommender/tag_filter.py`:
- THEMATIC_TAGS
- NON_THEMATIC_PATTERNS
- TAG_ALIASES

El script genera un informe CSV en: `data/processed/tag_report.csv`

Cada vez que se ejecuta se sobreescribe el archivo.

## Ejecutarlo

Desde el directorio `proyecto_ii` ejecutar:

* `python -m scripts_pruebas.check_loader`
* `python -m scripts_pruebas.check_recommender`
* `python -m scripts_pruebas.inspect_tags`


