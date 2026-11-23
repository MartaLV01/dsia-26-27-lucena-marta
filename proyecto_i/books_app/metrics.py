from books_app.validator import BookRecord

class BooksMetrics:
    """Open/Closed: se pueden añadir métricas sin tocar el validador."""

    def total_books(self, books: list[BookRecord]) -> int:
        """Devuelve el número de libros válidos."""
        return len(books)

    def average_rating(self, books: list[BookRecord]) -> float:
        """Devuelve la valoración media de los libros."""
        if not books:
            return 0.0

        return sum(book.average_rating for book in books) / len(books)

    def most_rated_book(self, books: list[BookRecord]) -> BookRecord | None:
        """Devuelve el libro con más valoraciones."""
        if not books:
            return None

        return max(books, key=lambda book: book.ratings_count)
