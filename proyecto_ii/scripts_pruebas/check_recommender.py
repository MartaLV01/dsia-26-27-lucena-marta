
"""
Script de comprobación del recomendador de libros.

Carga un modelo previamente entrenado y permite
comprobar los tres modos de recomendación:
- A partir de libros seleccionados.
- A partir de etiquetas temáticas.
- Combinando libros y etiquetas.
"""

from pathlib import Path
from time import perf_counter

import pandas as pd

from book_recommender.model_training import load_model
from book_recommender.logging_config import setup_logging


setup_logging()

# 1. Cargar el catálogo
data_path = Path("data/processed/books_master.csv")
books = pd.read_csv(data_path)

print(f"Libros cargados: {len(books)}")

# 2. Cargar el modelo actualizado
# use el comando:
#       python -m book_recommender.cli --model-output artifacts/book_recommender_tags_test.joblib
# para crear el moelo que vamos a ver ahora

# CAMBIAR ESTA RUTA SI EL CLI SE EJECUTA Y PONE OTRO NOMBRE EL JOBLIB
model_path = Path("artifacts/book_recommender_tags_test.joblib")
recommender = load_model(model_path)

print("\nModelo cargado correctamente.")


def show_recommendations(description, book_ids=None, tags=None):
    """Genera y muestra recomendaciones para una consulta."""

    start = perf_counter()

    recommendations = recommender.recommend(
        book_ids=book_ids,
        tags=tags,
        n_recommendations=5,
    )

    recommendation_time = perf_counter() - start

    print(f"\n{'=' * 70}")
    print(description)
    print(f"{'=' * 70}")

    print(f"Libros de referencia: {book_ids}")
    print(f"Etiquetas utilizadas: {tags}")
    print(f"Tiempo: {recommendation_time:.4f} segundos")

    if recommendations.empty:
        print("\nNo se han encontrado recomendaciones.")
        return

    print("\nLibros recomendados:")

    print(
        recommendations[
            ["book_id", "title", "authors", "similarity"]
        ].to_string(index=False)
    )


# 3. Modo 1: recomendaciones a partir de un libro.
show_recommendations(
    description="MODO 1: RECOMENDACIONES A PARTIR DE UN LIBRO",
    book_ids=[1],
)


# 4. Modo 2: recomendaciones a partir de etiquetas.
show_recommendations(
    description="MODO 2: RECOMENDACIONES A PARTIR DE ETIQUETAS",
    tags=["romance", "historical-fiction"],
)


# 5. Modo 3: combinación de libros y etiquetas.
show_recommendations(
    description="MODO 3: RECOMENDACIONES COMBINADAS",
    book_ids=[10],
    tags=["romance", "historical-fiction"],
)




"""

ESTO ERA PARA CUANDO USABA EL TITULO Y AUTOR, LO QUE PODIA HACER QUE SE DIERA
 MAS PESOS A ELLOS QUE A LAS TAGS, QUE ERA LO  QUE REALMENTE QUIERO MEDIR Y RECOMENDAR

Script de comprobación del recomendador de libros.

Carga un modelo previamente entrenado y permite
comprobar las recomendaciones generadas.
"""
"""
from pathlib import Path
from time import perf_counter

import pandas as pd

from book_recommender.model_training import load_model
from book_recommender.logging_config import setup_logging


setup_logging()

# 1. Cargar el catálogo.
data_path = Path("data/processed/books_master.csv")
books = pd.read_csv(data_path)

print(f"Libros cargados: {len(books)}")

# 2. Cargar el modelo previamente entrenado.
model_path = Path("artifacts/book_recommender_cli_test.joblib")

recommender = load_model(model_path)

print("\nModelo cargado correctamente.")

# 3. Elegir un libro real del catálogo.
selected_book = books.iloc[0]
book_id = int(selected_book["book_id"])

tags = [
    selected_book[column]
    for column in ["tag_1", "tag_2", "tag_3", "tag_4", "tag_5"]
    if pd.notna(selected_book[column])
][:2]

print(f"\nLibro seleccionado: {selected_book['title']}")
print(f"Etiquetas utilizadas: {tags}")

# 4. Generar recomendaciones.
start = perf_counter()

recommendations = recommender.recommend(
    book_ids=[book_id],
    tags=tags,
    n_recommendations=5,
)

recommendation_time = perf_counter() - start

print(f"\nTiempo de recomendación: {recommendation_time:.4f} segundos")
print("\nLibros recomendados:")

print(
    recommendations[
        ["title", "authors", "similarity"]
    ].to_string(index=False)
)
"""