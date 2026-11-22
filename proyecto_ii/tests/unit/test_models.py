
import pytest
from pydantic import ValidationError

from book_recommender.models import (
    BookRecord, RatingRecord, BookTagRecord,
    TagRecord, ToReadRecord,
)


# BookRecord

def test_book_record_valid():
    book = BookRecord(
        book_id=1,
        goodreads_book_id=2767052,
        best_book_id=1,
        work_id=2792775,
        books_count=272,
        isbn="0439023483",
        isbn13="9780439023480",
        authors="Suzanne Collins",
        original_publication_year=2008,
        original_title="The Hunger Games",
        title="The Hunger Games",
        language_code="eng",
        average_rating=4.34,
        ratings_count=4780653,
        work_ratings_count=4942365,
        work_text_reviews_count=155254,
        ratings_1=66715,
        ratings_2=127936,
        ratings_3=560092,
        ratings_4=1481305,
        ratings_5=2706317,
        image_url=None,
        small_image_url=None,
    )

    assert book.book_id == 1
    assert book.title == "The Hunger Games"
    assert book.average_rating == 4.34


def test_book_record_invalid_id():
    with pytest.raises(ValidationError):
        BookRecord(
            book_id=0,
            goodreads_book_id=2767052,
            best_book_id=1,
            work_id=2792775,
            books_count=272,
            authors="Suzanne Collins",
            title="The Hunger Games",
            average_rating=4.34,
            ratings_count=100,
            work_ratings_count=100,
            work_text_reviews_count=10,
            ratings_1=0,
            ratings_2=0,
            ratings_3=10,
            ratings_4=40,
            ratings_5=50,
        )


def test_book_record_invalid_average_rating():
    with pytest.raises(ValidationError):
        BookRecord(
            book_id=1,
            goodreads_book_id=2767052,
            best_book_id=1,
            work_id=2792775,
            books_count=272,
            authors="Suzanne Collins",
            title="The Hunger Games",
            average_rating=6,
            ratings_count=100,
            work_ratings_count=100,
            work_text_reviews_count=10,
            ratings_1=0,
            ratings_2=0,
            ratings_3=10,
            ratings_4=40,
            ratings_5=50,
        )


def test_book_record_optional_isbn():
    book = BookRecord(
        book_id=1,
        goodreads_book_id=2767052,
        best_book_id=1,
        work_id=2792775,
        books_count=272,
        isbn=None,
        isbn13=None,
        authors="Suzanne Collins",
        title="The Hunger Games",
        average_rating=4.34,
        ratings_count=100,
        work_ratings_count=100,
        work_text_reviews_count=10,
        ratings_1=0,
        ratings_2=0,
        ratings_3=10,
        ratings_4=40,
        ratings_5=50,
    )

    assert book.isbn is None
    assert book.isbn13 is None


# RatingRecord

def test_rating_record_valid():
    rating = RatingRecord(
        user_id=1,
        book_id=1,
        rating=5,
    )

    assert rating.rating == 5


def test_rating_record_invalid_value():
    with pytest.raises(ValidationError):
        RatingRecord(
            user_id=1,
            book_id=1,
            rating=6,
        )


# BookTagRecord

def test_book_tag_record_valid():
    book_tag = BookTagRecord(
        goodreads_book_id=2767052,
        tag_id=30574,
        count=100,
    )

    assert book_tag.count == 100


def test_book_tag_record_invalid_count():
    with pytest.raises(ValidationError):
        BookTagRecord(
            goodreads_book_id=2767052,
            tag_id=30574,
            count=-1,
        )


# TagRecord

def test_tag_record_valid():
    tag = TagRecord(
        tag_id=1,
        tag_name="fantasy",
    )

    assert tag.tag_name == "fantasy"


def test_tag_record_invalid_name():
    with pytest.raises(ValidationError):
        TagRecord(
            tag_id=1,
            tag_name="   ",
        )


# ToReadRecord

def test_to_read_record_valid():
    to_read = ToReadRecord(
        user_id=1,
        book_id=1,
    )

    assert to_read.user_id == 1
    assert to_read.book_id == 1


def test_to_read_record_invalid_user():
    with pytest.raises(ValidationError):
        ToReadRecord(
            user_id=0,
            book_id=1,
        )
