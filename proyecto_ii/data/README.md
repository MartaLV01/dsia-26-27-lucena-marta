# Datos del proyecto

Este directorio contiene los datos utilizados y generados para desarrollar el sistema de recomendación de libros.

## Dataset: Goodbooks-10k

Los datos proceden del dataset **Goodbooks-10k**, creado por Zygmunt Zając, disponible en:

Repositorio original: https://github.com/zygmuntz/goodbooks-10k

Repositorio original Releases: https://github.com/zygmuntz/goodbooks-10k/releases

Licencia indicada por la fuente: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0). Conviene comprobar las condiciones de uso y redistribución en la fuente original antes de publicar datos derivados o muestras.

Licencia: https://creativecommons.org/licenses/by-sa/4.0/

Fecha de descarga: 13/10/26.

Para ejecutar el pipeline completo es necesario descargar los siguientes archivos CSV y colocarlos en `data/raw/`:

- `books.csv`: información y metadatos de los libros.
- `ratings.csv`: valoraciones realizadas por los usuarios.
- `book_tags.csv`: relación entre libros y etiquetas.
- `tags.csv`: información de las etiquetas disponibles.
- `to_read.csv`: libros que los usuarios han añadido a su lista de lectura.

## Organización

- `raw/`: contiene los archivos CSV originales, sin modificar.
- `processed/`: contiene los datos generados durante las fases de validación, transformación y preparación.

## Consideraciones

Los archivos originales completos no se incluyen en este repositorio. Cada usuario debe descargarlos desde la fuente indicada y colocarlos en `raw/`

Las muestras de datos, si se incluyen, se utilizarán para facilitar la comprensión del proyecto y ejecutar pruebas sin necesidad de descargar el dataset completo.

Para mas informacion consultar el README de cada subdirectorio.