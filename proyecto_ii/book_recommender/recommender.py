

"""
Sistema de recomendación de libros basado en contenido.

Utiliza TF-IDF para representar los textos de los libros
y NearestNeighbors para encontrar libros similares.
"""

import logging

import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize


logger = logging.getLogger(__name__)


class BookRecommender:
    """Recomendador de libros basado en similitud textual."""


    # algorithm="brute" no calcula todas las distancias durante fit()
    # La búsqueda de vecinos se realiza cuando llamamos a kneighbors()
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer()
        self.nearest_neighbors = NearestNeighbors(
            metric="cosine",
            algorithm="brute",
        )

        self.books_ = None
        self.tfidf_matrix_ = None
        self.is_fitted_ = False

    def fit(self, books: pd.DataFrame):
        """
        Entrena 
            TF-IDF (transforma el texto en vectores)
            NearestNeighbors (busca los libros similares
            mas cercanos con los vectores del TF-IDF)
        con el catálogo de libros.

        Args:
            books: DataFrame con book_id, title y content.

        Returns:
            La propia instancia del recomendador.
        """
        required_columns = {"book_id", "title", "content"}
        missing_columns = required_columns - set(books.columns)

        if missing_columns:
            raise ValueError(
                f"Faltan columnas necesarias: {sorted(missing_columns)}"
            )

        if books.empty:
            raise ValueError("El catálogo de libros está vacío.")

        if books["book_id"].duplicated().any():
            raise ValueError("Existen identificadores de libros duplicados.")

        contents = books["content"].fillna("").astype(str)

        if not contents.str.strip().any():
            raise ValueError("No hay contenido textual para entrenar.")

        logger.info("Entrenando recomendador: books=%s", len(books))

        self.books_ = books.reset_index(drop=True).copy()

        # 1_ transformo los textos en vectores TF-IDF.
        self.tfidf_matrix_ = self.vectorizer.fit_transform(contents)

        # 2_ entreno la búsqueda de vecinos con los datos conseguidos con el TF-IDF
        self.nearest_neighbors.fit(self.tfidf_matrix_)

        self.is_fitted_ = True

        logger.info(
            "Recomendador entrenado: books=%s, features=%s",
            self.tfidf_matrix_.shape[0],
            self.tfidf_matrix_.shape[1],
        )

        return self

    def recommend(
        self,
        book_ids: list[int] | None = None, 
        tags: list[str] | None = None,
        n_recommendations: int = 5,
    ) -> pd.DataFrame:
        """
        Recomienda libros a partir de libros y/o etiquetas.
        Puede hacer recomendaciones
        - en base solo a libros
        - en base a etiquetas
        - en base a libros y etiquetas

        Args:
            book_ids: identificadores de los libros que gustan al usuario.
            tags: géneros o etiquetas de interés.
            n_recommendations: número máximo de recomendaciones.

        Returns:
            DataFrame con los libros recomendados y su similitud.
        """
        if not self.is_fitted_:
            raise RuntimeError("El recomendador todavía no está entrenado")

        if n_recommendations < 1:
            raise ValueError("El número de recomendaciones debe ser positivo")

        book_ids = book_ids or []
        tags = [tag.strip() for tag in (tags or []) if tag.strip()]

        if not book_ids and not tags:
            raise ValueError(
                "Debes proporcionar al menos un libro o una etiqueta"
            )

        # Localizamos los libros seleccionados
        book_positions = {
            book_id: position
            for position, book_id in enumerate(self.books_["book_id"])
        }

        unknown_ids = set(book_ids) - set(book_positions)

        if unknown_ids:
            raise ValueError(
                f"No se encuentran estos identificadores: {sorted(unknown_ids)}"
            )

        profile_parts = []

        # Perfil construido a partir de los libros elegidos
        if book_ids:
            positions = [book_positions[book_id] for book_id in book_ids]

            book_profile = csr_matrix(
                self.tfidf_matrix_[positions].mean(axis=0)
            )

            profile_parts.append(normalize(book_profile))

        # Perfil construido a partir de las etiquetas elegidas
        if tags:
            tag_profile = self.vectorizer.transform([" ".join(tags)])

            if tag_profile.nnz == 0:
                raise ValueError(
                    "Las etiquetas proporcionadas no aparecen "
                    "en el vocabulario del catálogo."
                )

            profile_parts.append(normalize(tag_profile))

        # Si hay libros y etiquetas, combinamos ambos perfiles.
        if len(profile_parts) == 2:
            profile = normalize(profile_parts[0] + profile_parts[1])
        else:
            profile = profile_parts[0]

        # Buscamos los libros más cercanos al perfil.
        distances, indices = self.nearest_neighbors.kneighbors(
            profile,
            n_neighbors=len(self.books_),
        )

        liked_ids = set(book_ids)
        recommendations = []

        for distance, position in zip(distances[0], indices[0]):
            book = self.books_.iloc[position]
            book_id = book["book_id"]

            # No recomendamos libros que el usuario ya ha seleccionado.
            if book_id in liked_ids:
                continue

            recommendations.append(book.to_dict() | {
                "similarity": float(1 - distance)
            })

            if len(recommendations) == n_recommendations:
                break

        result = pd.DataFrame(recommendations)

        logger.info(
            "Recomendaciones generadas: requested=%s, returned=%s",
            n_recommendations,
            len(result),
        )

        return result
