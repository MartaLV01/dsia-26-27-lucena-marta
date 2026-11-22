# Datos procesados

Esta carpeta almacenará los archivos generados por el pipeline durante las fases de limpieza, transformación y preparación de los datos.

A partir de los archivos originales de `data/raw/`, el proyecto podrá generar conjuntos de datos preparados para:
- Construir el conjunto de datos maestro de libros.
- Preparar las características temáticas utilizadas por el recomendador.
- Entrenar el modelo de recomendación.
- Evaluar el rendimiento del sistema mediante métricas de similitud, diversidad y cobertura del catálogo.

Los archivos de esta carpeta son resultados derivados del procesamiento y no forman parte del dataset original Goodbooks-10k.

**Nota:** los archivos generados se crearán al ejecutar el pipeline y no es necesario incluirlos en el repositorio. Se podrán consultar los resultados de evaluación versionados en esta carpeta.