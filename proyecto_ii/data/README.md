# Datos del proyecto

Este directorio contiene los datos utilizados para desarrollar el sistema de recomendación de libros.

## Dataset: Goodbooks-10k

Los datos proceden del dataset **Goodbooks-10k**, disponible en:

https://github.com/zygmuntz/goodbooks-10k/releases

Licencia indicada por la fuente: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). Conviene comprobar las condiciones de uso y redistribución en la fuente original antes de publicar datos derivados o muestras.

Fecha de descarga: 13/10/26.

Para ejecutar el pipeline completo es necesario descargar los siguientes archivos CSV y colocarlos en `data/raw/`:

- `books.csv`: información y metadatos de los libros.
- `ratings.csv`: valoraciones realizadas por los usuarios.
- `book_tags.csv`: relación entre libros y etiquetas.
- `tags.csv`: información de las etiquetas disponibles.
- `to_read.csv`: libros que los usuarios han añadido a su lista de lectura.

## Organización

- `raw/`: contiene los archivos CSV originales, sin modificar.
- `processed/`: contiene los datos generados durante las fases de limpieza y preparación.

## Consideraciones

Los archivos originales completos no se incluyen en este repositorio. Cada usuario debe descargarlos desde la fuente indicada y colocarlos en la carpeta correspondiente.

Las muestras de datos, si se incluyen, se utilizarán para facilitar la comprensión del proyecto y ejecutar pruebas sin necesidad de descargar el dataset completo.

**Nota:** consultar las condiciones de uso y redistribución del dataset en su fuente original.