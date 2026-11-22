# Logs

Esta carpeta almacena los registros de ejecución del pipeline.

Los logs permiten consultar:

- Las etapas ejecutadas.
- El estado de cada operación.
- Los errores y advertencias detectados.
- El tiempo de ejecución y otra información de diagnóstico.

Los archivos se generan automáticamente al ejecutar el pipeline y se organizan por fecha: `pipeline_YYYY-MM-DD.log`

La configuración del sistema de logging se encuentra en `book_recommender/logging_config.py`.

No se deben incluir credenciales, tokens ni información sensible en los registros.