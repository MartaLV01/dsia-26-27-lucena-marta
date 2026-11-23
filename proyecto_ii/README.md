# Proyecto II - Books App

## Descripción
Este proyecto desarrolla un sistema de recomendación de libros basado en contenido.

El objetivo es recomendar libros similares a otros libros o a unas preferencias temáticas determinadas, utilizando las etiquetas asociadas a cada libro.

Para ello se utiliza el dataset público Goodbooks-10k, creado por Zygmunt Zając.

- **Fuente**: https://github.com/zygmuntz/goodbooks-10k
- **Licencia indicada por la fuente**: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
- **Fecha de descarga**: 13/10/26.
- **Ubicación de los archivos originales**: `data/raw`
- **Muestra incluida en el repositorio**: en el repositorio no se ha subido ninguna muestra. Para obtener instrucciones sobre su descarga, consultar `data/raw/README.md`

Para informacion mas detallada ir a los README.md de las carpetas.

El sistema procesa los datos originales, valida su contenido, prepara un conjunto de datos maestro y construye un modelo de recomendación utilizando exclusivamente las etiquetas temáticas de los libros.

El modelo utiliza TF-IDF para representar las etiquetas como vectores numéricos y NearestNeighbors con similitud coseno para encontrar libros similares.

El proyecto incluye un pipeline reproducible, una interfaz de línea de comandos (CLI), persistencia del modelo mediante Joblib, evaluación de recomendaciones y tests automatizados.

### Funcionamiento del sistema

El pipeline se organiza en las siguientes fases:

1. **Carga de datos**: lectura de los cinco archivos CSV originales.
2. **Validación**: comprobación de los datos y aplicación de reglas de negocio. Se identifican los registros válidos e inválidos.
3. **Preparación**: limpieza y transformación de los datos, clasificación de etiquetas y construcción del conjunto de datos maestro.
4. **Extracción de características**: selección de las cinco etiquetas temáticas principales de cada libro.
5. **Entrenamiento**: construcción de la representación TF-IDF y entrenamiento del modelo NearestNeighbors.
6. **Persistencia**: almacenamiento del modelo entrenado en formato .joblib.
7. **Evaluación**: generación de consultas de prueba y cálculo de métricas para analizar el comportamiento del recomendador.

### Reglas de validación

Durante la validación de los datos se comprueba, entre otros aspectos, que:
- Los identificadores y books_count sean enteros positivos.
- average_rating esté entre 0 y 5, ambos incluidos.
- ratings_count sea un entero no negativo.
- authors y title no sean nulos ni estén vacíos.
- Estén presentes todas las columnas obligatorias.
- El campo isbn puede ser nulo.
- No hay duplicados.

También se realizan comprobaciones adicionales de integridad y consistencia entre los distintos conjuntos de datos.

### Sistema de recomendación
El recomendador utiliza un enfoque basado en contenido.

Las características empleadas para representar cada libro son sus cinco etiquetas temáticas principales (tag_1 a tag_5).

No se utilizan las valoraciones de los usuarios para entrenar el recomendador ni para calcular las recomendaciones.

#### Representación de los libros

Las etiquetas temáticas se transforman mediante TF-IDF (Term Frequency-Inverse Document Frequency), obteniendo una representación numérica de cada libro.

#### Búsqueda de libros similares

Se utiliza NearestNeighbors de scikit-learn con distancia coseno para localizar los libros más similares a una consulta.

#### Modos de recomendación

El sistema permite realizar tres tipos de consultas:
- **Por libro**: utiliza uno o varios identificadores de libros como referencia.
- **Por etiquetas**: utiliza etiquetas temáticas proporcionadas como consulta.
- **Combinada**: combina identificadores de libros y etiquetas temáticas.

El sistema devuelve una lista de cinco libros recomendados.

### Métricas
El proyecto calcula métricas descriptivas sobre el catálogo y métricas de diagnóstico sobre el recomendador.

Las metricas descriptivas tienen una finalidad descriptiva y no intervienen en el entrenamiento del modelo ni en la generación de recomendaciones.

1. Sobre los libros válidos se calculan:
    - Número total de libros válidos.
    - Valoración media.
    - Libro con mayor número de valoraciones.

2. Sobre el modelo creado:
    - Similitud media entre las consultas y los libros recomendados
    - Diversidad intra-lista, que analiza la variedad de libros dentro de las listas de recomendaciones
    - Cobertura del catálogo, que mide la proporción de libros distintos del catálogo que aparece en el conjunto de recomendaciones evaluado

**Justificación de las métricas**

El modelo es no supervisado y su objetivo es encontrar libros similares a partir de sus características textuales, no predecir una variable objetivo ni asignar clases conocidas.

Por este motivo las metricas de _R^2_, _MAE_, _RMSE_, _ConfussionMatrix_ o _Recall_ no las puedo usar.

En su lugar, se utilizan métricas de diagnóstico que permiten analizar la similitud de las recomendaciones, la variedad de los resultados y la cobertura del catálogo.

Estas métricas permiten estudiar el comportamiento del sistema, aunque no demuestran por sí solas que las recomendaciones sean relevantes para los usuarios.

**Proceso de evaluación**

La evaluación genera consultas reproducibles para los tres modos de recomendación:
- 20 consultas por identificadores de libros.
- 20 consultas por etiquetas.
- 20 consultas combinadas.

Se utiliza una semilla fija (random_state=42) para facilitar la reproducibilidad.

En total se evalúan 60 consultas, obteniendo hasta cinco recomendaciones por consulta.

Los resultados se almacenan en archivos JSON dentro de `data/processed/`.

**En la ultima ejecución**

| Tipo de consulta | Similitud media | Diversidad intra-lista | Cobertura |
|---|---:|---:|---:|
| Por libro | 0,9716 | 0,0260 | 1 % |
| Por etiquetas | 0,7331 | 0,1583 | 1 % |
| Combinada | 0,7374 | 0,1322 | 1 % |

Los resultados muestran diferencias interesantes: las consultas por libro obtienen una similitud muy elevada, pero una diversidad menor. Las consultas por etiquetas ofrecen recomendaciones más variadas.

La cobertura del 1 % también merece un análisis posterior: significa que el conjunto de recomendaciones de las consultas evaluadas recupera una parte pequeña del catálogo.

## Estructura del proyecto

```text
dsia/
├── proyecto_ii/
    ├── book_recommender/
    │   ├── __init__.py
    │   ├── loader.py
    │   ├── validator.py
    │   ├── dataset_builder.py
    │   ├── tag_filter.py
    │   ├── features.py
    │   ├── recommender.py
    │   ├── model_training.py
    │   ├── metrics.py
    │   ├── evaluation.py
    │   ├── pipeline.py
    │   ├── cli.py
    │   ├── logging_config.py
    │   └── models.py
    ├── data/
    │   ├── raw/
    │   └── processed/
    ├── artifacts/
    ├── logs/
    ├── scripts_pruebas/
    ├── tests/
    │   ├── unit/
    │   └── integration/
    ├── pytest.ini
    └── README.md
├── .gitignore
└── requirements.txt
```

Los directorios `raw/`, `processed/`, `artifacts/` y `logs/` contienen archivos de entrada o resultados generados. Sus respectivos README explican su contenido y utilización.

## Requisitos

- Python 3.12 o 3.13
- Dependencias especificadas en `requirements.txt`

## Instalación

El entorno virtual se encuentra en la raíz del repositorio (`dsia`).

Desde Git Bash, situarse en la raíz `dsia` y activar el entorno virtual:

```bash
source .venv/Scripts/activate
```

Después, instalar las dependencias de la aplicación:

```bash
python -m pip install -r requirements.txt
```

## Ejecución de la aplicación
Antes de ejecutar el proyecto es necesario disponer de los cinco archivos originales del dataset en data/raw/.

Desde la carpeta `proyecto_ii`:

```bash
python -m book_recommender.cli --data-dir data/raw --output data/processed/books_master.csv --model-output artifacts/book_recommender.joblib
```
Los argumentos permiten especificar:
- `--data-dir`: directorio que contiene los CSV originales.
- `--output`: ruta del conjunto de datos maestro generado.
- `--model-output`: ruta donde se guarda el modelo entrenado.
- `--log-level`: nivel de detalle de los registros de ejecución.

Para mas informacion sobre los comandos se puede ejecutar:

```bash
python -m book_recommender.cli --help
```

El pipeline genera también los resultados de evaluación y los logs de ejecución.

## Tests

Los tests se encuentran en la carpeta `tests/` y están organizados en pruebas unitarias y de integración.

Ejecutarlos desde `proyecto_ii`

Ejecutar todos los tests:

```bash
python -m pytest -q
```

Ejecutar los tests unitarios, excluyendo los de integración:

```bash
python -m pytest -q -m "not integration"
```

Ejecutar solo los tests de integración:

```bash
python -m pytest -q -m "integration"
```

## Cobertura de código

Para ejecutar los tests y medir la cobertura (desde `proyecto_ii`):

```bash
python -m pytest --cov=book_recommender --cov-report=term-missing --cov-fail-under=60
```

El umbral mínimo exigido es del 60 %.

En la última ejecución completa se obtuvieron 123 tests superados y una cobertura del 92,24 %.

## Scripts de comprobación manual

La carpeta `scripts_pruebas/` contiene herramientas auxiliares utilizadas durante el desarrollo para comprobar el funcionamiento de determinados módulos.

Estos scripts no sustituyen a los tests automatizados de `tests/`.

Consultar `scripts_pruebas/README.md` para obtener instrucciones de ejecución.

## Dependencias

Las dependencias del proyecto están documentadas en `requirements.txt`.

Entre las principales bibliotecas utilizadas se encuentran:
- pandas: carga y manipulación de los datos.
- scikit-learn: extracción de características TF-IDF y búsqueda de vecinos.
- joblib: persistencia y carga del modelo.
- pytest: ejecución de pruebas automatizadas.
- pytest-cov: medición de cobertura de código.

## Integración continua (CI)

El proyecto utiliza GitHub Actions para ejecutar automáticamente los tests y comprobar que la cobertura de código sea de al menos el 60 %.

Workflow: https://github.com/MartaLV01/dsia-26-27-lucena-marta/actions/workflows/ci.yml

Evidencia de ejecución correcta: https://github.com/MartaLV01/dsia-26-27-lucena-marta/actions/runs/45084985975

El workflow se ejecuta al subir cambios a las ramas main, proyecto1 y proyecto2, así como al abrir un Pull Request.

## Relación con el Proyecto III

Este proyecto constituye la base del futuro Proyecto III.
