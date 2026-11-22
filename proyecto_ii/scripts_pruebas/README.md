# Carpeta de apoyo

Los archivos contenidos en esta carpeta son usados para ver que las files principales funcionan correctamente.

## `check_loader.py`
Comprueba que los archivos de `data/` se leen correctamente con el `loader.load_data()`

## `check_recommender.py`
Primero hay que ejecutar el proeycto para poder obtener un .joblib

Permite comprobar los tres modos de recomendación utilizando un modelo ya entrenado.

Hay que cambiar la direccion del modelo .joblib dependiendo que que modelo sea el que se quiera probar
Se crea un modelo nuevo con:
       `python -m book_recommender.cli --model-output artifacts/book_recommender_tags_test.joblib`
En funcion de la ruta indicada se debe modificar esta otra ruta:
    `model_path = Path("artifacts/book_recommender_tags_test.joblib")`

## `inspect_tags.py`
El archivo `inspect_tags.py` se ha usado para ver que tags son los mas usados, categorias, mas frecuentes presentes en `tags.csv`teniendo en cuenta a que libro/s pertenece definido en `book_tags.csv`.

Esta viendo el rendimiento de `book_recommender/tag_filter.py` en funcion de las tags que ha ido imprimeirndo por consola he ido modificando las constantes: `THEMATIC_TAGS`, `NON_THEMATIC_PATTERNS`, `TAG_ALIASES`

Cada vez que se ejecuta se sobreescribe el archivo de salida:
    `output_path = Path("data/processed/tag_report.csv")`


## Ejecutarlo

Desde `~/dsia-26-27-lucena-marta/proyecto_ii` ejecutar las files

* `python -m scripts_pruebas.check_loader`
* `python -m scripts_pruebas.check_recommender`
* `python -m scripts_pruebas.inspect_tags`


