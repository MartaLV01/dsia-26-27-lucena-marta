"""
Métricas y agregaciones sobre los libros validados y el recomendador
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from book_recommender.recommender import BookRecommender

class BooksMetrics:
    """Calcula métricas sobre los libros válidos"""

    def total_books(self, books: pd.DataFrame) -> int:
        """Devuelve el número de libros válidos."""
        return len(books)

    def average_rating(self, books: pd.DataFrame) -> float:
        """Devuelve la valoración media de los libros."""
        if books.empty:
            return 0.0

        return float(books["average_rating"].mean())

    def most_rated_book(self, books: pd.DataFrame) -> pd.Series | None:
        """Devuelve el libro con más valoraciones."""
        if books.empty:
            return None

        return books.loc[books["ratings_count"].idxmax()]


class RecommenderMetrics:
    """Evalúa el comportamiento del recomendador"""

    def average_similarity(self, recommendations: pd.DataFrame) -> float:
        """
        Calcula la similitud media de los libros recomendados

        Args:
            recommendations: DataFrame generado por recommend()

        Returns:
            Similitud media entre 0 y 1
        """
        # si no hay libros recomendados
        if recommendations.empty:
            return 0.0

        # En recomendations tengo una columna con la similitud de cada libro recomendado hacia
        # el que me dieron
        if "similarity" not in recommendations.columns:
            raise ValueError("Las recomendaciones deben incluir la columna 'similarity'")

        # hace la media de todas las similitudes de los libros recomendados
        avg_similarity = float(recommendations["similarity"].mean())
        return avg_similarity
        #return float(recommendations["similarity"].mean())
    
    def intra_list_diversity(self, recommendations: pd.DataFrame, recommender: BookRecommender) -> float:
        """
        Calcula la diversidad media entre los libros recomendados

        Args:
            recommendations: DataFrame con los libros recomendados
            recommender: Recomendador entrenado con su matriz TF-IDF

        Returns:
            Distancia coseno media entre las parejas de libros
        """
        # Comprobamos que haya 2 o mas libros (es decir si no hay libros o solo hay uno),
        # ya que si no, no se puede ver la similitud entre los libros recomendados 
        if recommendations.empty or len(recommendations) < 2:
            return 0.0

        if "book_id" not in recommendations.columns:
            raise ValueError("Las recomendaciones deben incluir la columna 'book_id'")

        if recommendations["book_id"].duplicated().any():
            raise ValueError("Las recomendaciones contienen identificadores duplicados")

        if not recommender.is_fitted_:
            raise RuntimeError("El recomendador todavía no está entrenado")

        # recommender tiene: 
        # books_: el catálogo de libros utilizado para entrenarlo
        # tfidf_matrix_: la matriz que contiene los vectores TF-IDF de esos libros
        # is_fitted_: indica si se ha entrenado o no


        # TF-IDF trabaja sobre las posiciones de los libros (que recibio del dataframe al entrenar), no sobre los ids
        # por ello tenemos que sacar para cada id su posicion en la lista original ya que 
        # cada fila corresponde a la posición de un libro en recommender.books_
        # primero estamos creando un diccionario clave-valor con todos los libros de mi csv (modelo entrenado)
        # y su posicion en la lista
        book_positions = {
            book_id: position
            for position, book_id in enumerate(recommender.books_["book_id"])
        }

        # Segundo miramos si hay ids no encontrados
        unknown_ids = (set(recommendations["book_id"]) - set(book_positions))

        if unknown_ids:
            raise ValueError(f"No se encuentran estos identificadores: {sorted(unknown_ids)}")

        # tercero obtenemos la posicion de las recoemndaciones en la lista de libros del modelo
        positions = [
            book_positions[book_id]
            for book_id in recommendations["book_id"]
        ]

        # con la lista de posiciones recuperamos los vectores (contienen la info usada en el TF-IDF de cada libro)
        vectors = recommender.tfidf_matrix_[positions]

        # calcula la similitud coseno libro vs libro 
        # -> consigue una matriz donde la diagonal es 1 (similitud de un libro consigo mismo)
        similarity_matrix = cosine_similarity(vectors)

        # esas similitudes se pasan a distancias -> 
        # una distancia cercana a 1 indica que son diferentes
        # cercano a 0 seran libros similares
        distances = 1 - similarity_matrix

        # como la matriz es simetrica (la distancia entre A-B es la misma que entre B-A)
        # no necesitamos toda la matriz, sino solo el triangulo superior o inferior
        # en este caso cogemos el superior
        upper_triangle = distances[
            # pd.np.triu_indices(len(positions), k=1)
            np.triu_indices(len(positions), k=1)
        ]

        # Clacula la distancia media entre todas las parejas
        # de libros recomendados: cuanto mayor sea, más diversa es la lista.
        avg_diversity_recommended_list = float(upper_triangle.mean())
        return avg_diversity_recommended_list
        #return float(upper_triangle.mean())

    def catalog_coverage(self, recommendations_list: list[pd.DataFrame], catalog_size: int) -> float:
        """
        Calcula la proporcion del catalogo de libros que aparece ne las recomendaciones

        Args:
            recommendations_list: Lista de dataframes con las reocmendaciones de diversas recoemndaciones
            catalog_size: Numeor total de libros del catalogo

        Returns:
            Cuanto cubre el catalogo entre 0 y 1
        """
        if catalog_size <= 0:
            raise ValueError("El tamaño del catálogo debe ser mayor que cero")

        if not recommendations_list:
            return 0.0

        # se hace con un set ya que asi si hay libros repetidos solo se cuentan una vez
        recommended_ids = set()

        for recommendations in recommendations_list:
            if "book_id" not in recommendations.columns:
                raise ValueError("Las recomendaciones deben contener la columna 'book_id'")

            recommended_ids.update(recommendations["book_id"].dropna())

        return len(recommended_ids) / catalog_size

