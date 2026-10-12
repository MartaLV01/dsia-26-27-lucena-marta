# Proyecto I — Aplicación de ventas

## Descripción

Aplicación Python para cargar, validar y procesar datos de ventas mediante una arquitectura modular.

El proyecto separa las responsabilidades en los siguientes módulos:

- `loader.py`: carga los datos de ventas desde un CSV.
- `validator.py`: valida los datos y separa las filas válidas de las inválidas.
- `metrics.py`: calcula agregaciones, como el importe total por región.
- `cli.py`: permite ejecutar la aplicación desde la línea de comandos.

## Estructura del proyecto

```text
dsia-26-27-lucena-marta
├──proyecto_i/
    ├── data/
    ├── tests/
    │   └── ventas/
    │       ├── test_loader.py
    │       ├── test_validator.py
    │       ├── test_metrics.py
    │       ├── test_integration.py
    │       └── test_cli.py
    ├── ventas_app/
    │   ├── __init__.py
    │   ├── loader.py
    │   ├── validator.py
    │   ├── metrics.py
    │   └── cli.py
    ├── pytest.ini
    └── README.md
├── requirements.txt
└── README.md
```

## Requisitos

- Python
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

Desde la carpeta `proyecto_i`:

```bash
python -m ventas_app.cli --input data/ventas.csv --output data/ventas_limpias.csv
```

Los argumentos `--input` y `--output` indican el fichero CSV de entrada y el fichero de salida, respectivamente.

## Tests

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
python -m pytest -q -m integration
```

## Cobertura de código

Para ejecutar los tests y medir la cobertura:

```bash
python -m pytest --cov=ventas_app --cov-report=term-missing --cov-fail-under=60
```

El umbral mínimo exigido es del 60 %.

## Organización de los tests

- `test_loader.py`: comprueba la carga correcta y el tratamiento de rutas inexistentes.
- `test_validator.py`: comprueba la separación de filas válidas e inválidas y los casos límite.
- `test_metrics.py`: verifica las agregaciones con resultados conocidos.
- `test_cli.py`: comprueba el funcionamiento del punto de entrada.
- `test_integration.py`: comprueba el procesamiento de los datos reales de ventas.

## Integración

El test de integración utiliza el CSV de ventas del curso para verificar los resultados esperados: 140 filas válidas y 10 filas inválidas.

## Dependencias

Las dependencias del proyecto están documentadas en `requirements.txt`, incluyendo `pytest` y `pytest-cov` para ejecutar y medir los tests.

## Integración continua (CI)

El proyecto utiliza GitHub Actions para ejecutar automáticamente los tests y comprobar que la cobertura de código sea de al menos el 60 %.

Workflow: https://github.com/MartaLV01/dsia-26-27-lucena-marta/actions/workflows/ci.yml

Evidencia de ejecución correcta: https://github.com/MartaLV01/dsia-26-27-lucena-marta/actions/runs/38318143302

El workflow se ejecuta al subir cambios a las ramas main y proyecto1, así como al abrir un Pull Request.