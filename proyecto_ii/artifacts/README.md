# Modelos entrenados

Esta carpeta almacena los modelos de recomendación entrenados y serializados durante la ejecución del pipeline.

El modelo se guarda en formato `.joblib` para permitir su posterior carga y utilización sin necesidad de volver a entrenarlo.

## Generación del modelo

Desde el directorio `proyecto_ii/`, ejecutar:

```bash
python -m book_recommender.cli \
    --data-dir data/raw \
    --output data/processed/books_master.csv \
    --model-output artifacts/book_recommender.joblib
```

El pipeline realiza las fases de carga, validación y preparación de los datos, entrena el recomendador y guarda el modelo en esta carpeta.

## Consideraciones

Los modelos serializados no se incluyen en el repositorio. Pueden generarse nuevamente ejecutando el pipeline con los datos originales disponibles en `data/raw/`.