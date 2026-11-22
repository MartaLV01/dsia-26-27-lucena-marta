# Datos procesados

Esta carpeta almacenará los archivos generados por el pipeline durante las fases de limpieza, transformación y preparación de los datos.

A partir de los archivos originales de `data/raw/`, el proyecto podrá generar conjuntos de datos preparados para:

- Entrenar los modelos de recomendación.
- Construir las características de libros y usuarios.
- Realizar predicciones de valoraciones.
- Generar y evaluar recomendaciones personalizadas.

Los archivos de esta carpeta son resultados derivados del procesamiento y no forman parte del dataset original Goodbooks-10k.

**Nota:** los archivos generados se crearán al ejecutar el pipeline y no es necesario incluirlos en el repositorio.