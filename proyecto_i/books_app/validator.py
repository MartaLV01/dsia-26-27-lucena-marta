from dataclasses import dataclass
import pandas as pd

POSITIVO = 0
MIN_RATE = 0
MAX_RATE = 5

class ValidationError(Exception):
    """Datos que no cumplen reglas de negocio."""

@dataclass(frozen=True)
class BookRecord:
    book_id: int  # es el id en el csv
    goodreads_book_id: int # es el id del libro en goodreads suele ser igual al best_book_id
    best_book_id: int # es el id del libro mejor en goodreads
    work_id: int  # es el id de la lista de libros con ese nombre o en otros idiomas/ediciones
    books_count: int # es el numero de libros
    isbn: str | None #puede ser un valor nulo. Str pq es un identificador que puede tener X o mepezar en 0
    authors: str
    title: str
    average_rating: float
    ratings_count: int

    #@property
    #def amount(self) -> float:
    #    return self.units * self.unit_price



class BookValidator:
    """Single Responsibility: solo valida."""

    def split(self, frame: pd.DataFrame) -> tuple[list[BookRecord], pd.DataFrame, pd.DataFrame]:
        required_columns = {
            "book_id",
            "goodreads_book_id",
            "best_book_id",
            "work_id",
            "books_count",
            "isbn", 
            "authors",
            "title", 
            "average_rating",
            "ratings_count"
        }

        missing_columns = required_columns - set(frame.columns)

        if missing_columns:
            raise ValidationError(
                f"Faltan columnas obligatorias: {sorted(missing_columns)}"
            )
        
        work = frame.copy()
        work["book_id"] = pd.to_numeric(work["book_id"], errors="coerce")
        work["goodreads_book_id"] = pd.to_numeric(work["goodreads_book_id"], errors="coerce")
        work["best_book_id"] = pd.to_numeric(work["best_book_id"], errors="coerce")
        work["work_id"] = pd.to_numeric(work["work_id"], errors="coerce")
        work["books_count"] = pd.to_numeric(work["books_count"], errors="coerce")
        work["average_rating"] = pd.to_numeric(work["average_rating"], errors="coerce")
        work["ratings_count"] = pd.to_numeric(work["ratings_count"], errors="coerce")

        integer_columns = [
            "book_id",
            "goodreads_book_id",
            "best_book_id",
            "work_id",
            "books_count",
            "ratings_count",
        ]

        valid_integers = pd.Series(True, index=work.index)

        #Compruebo que los int son int y no decimales
        for column in integer_columns:
            valid_integers &= (
                work[column].notna()
                & (work[column] % 1 == 0)
            )

        pass_validation = (valid_integers &
                           (work["book_id"] > POSITIVO) & 
                           (work["goodreads_book_id"] > POSITIVO) &
                           (work["best_book_id"] > POSITIVO) &
                           (work["work_id"] > POSITIVO) &
                           (work["books_count"] > POSITIVO) &
                           work["authors"].notna() & 
                           work["authors"].astype("string").str.strip().ne("") & 
                           work["title"].notna() & 
                           work["title"].astype("string").str.strip().ne("") &
                           work["average_rating"].notna() &
                           (work["average_rating"] >= MIN_RATE) &
                           (work["average_rating"] <= MAX_RATE) &
                           (work["ratings_count"] >= POSITIVO)
                           )

        valid_rows = []
        for row in work.loc[pass_validation].itertuples(index=False):
            isbn = str(row.isbn).strip() if pd.notna(row.isbn) else None

            if isbn == "":
                isbn = None

            valid_rows.append(
                BookRecord(
                    book_id=int(row.book_id),
                    goodreads_book_id=int(row.goodreads_book_id),
                    best_book_id=int(row.best_book_id),
                    work_id=int(row.work_id),
                    books_count=int(row.books_count),
                    isbn=isbn,

                    authors=str(row.authors),
                    title=str(row.title),

                    average_rating=float(row.average_rating),
                    ratings_count=int(row.ratings_count),
                )
            )

        return valid_rows, work.loc[pass_validation], work.loc[~pass_validation]
