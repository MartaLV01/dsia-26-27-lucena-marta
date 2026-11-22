
import pandas as pd
import pytest

from book_recommender.features import prepare_book_features


def test_prepare_book_features_combines_text():
    books = pd.DataFrame({
        # dado que ahora no uso el titulo ni el autor
        #"title": ["Harry Potter"],
        #"authors": ["J.K. Rowling"],
        "tag_1": ["fantasy"],
        "tag_2": ["magic"],
        "tag_3": [None],
        "tag_4": [None],
        "tag_5": [None],
    })

    result = prepare_book_features(books)

    assert result.loc[0, "content"] == (
        #"Harry Potter J.K. Rowling fantasy magic"
        "fantasy magic"
    )


def test_prepare_book_features_does_not_modify_original():
    # aunque titulo y autores ya no nos interesan, este test verifica
    # que el df original no sea modfificado
    books = pd.DataFrame({
        "title": ["Harry Potter"],
        "authors": ["J.K. Rowling"],
        "tag_1": ["fantasy"],
        "tag_2": ["magic"],
        "tag_3": [None],
        "tag_4": [None],
        "tag_5": [None],
    })

    original_columns = list(books.columns)

    prepare_book_features(books)

    assert list(books.columns) == original_columns
    assert "content" not in books.columns


def test_prepare_book_features_missing_column():
    # titulo y autores no nos interesan ya para le recomendador 
    # y por lo tanto no son columnas necesarias para el modelo
    # el test sigue pasando porque no se le indican las etiquetas 
    # y eso es algo necesario para el modelo
    books = pd.DataFrame({
        "title": ["Harry Potter"],
        "authors": ["J.K. Rowling"],
    })

    with pytest.raises(ValueError, match="Faltan columnas"):
        prepare_book_features(books)


def test_prepare_book_features_handles_null_values():
    # nuestro modelo ya no necesita el titulo o autor
    # por ellos el assert es un vacio ya que no le estamos poniendo etiquetas
    books = pd.DataFrame({
        #"title": [None],
        #"authors": ["J.K. Rowling"],
        "tag_1": [None],
        "tag_2": [None],
        "tag_3": [None],
        "tag_4": [None],
        "tag_5": [None],
    })

    result = prepare_book_features(books)

    #assert result.loc[0, "content"] == "J.K. Rowling"
    assert result.loc[0, "content"] == ""

def test_prepare_book_features_ignores_title_and_authors():
    # con este test se ve que ni titulo ni autor esten influenciando el modelo
    books = pd.DataFrame({
        "title": ["Harry Potter"],
        "authors": ["J.K. Rowling"],
        "tag_1": ["fantasy"],
        "tag_2": ["magic"],
        "tag_3": [None],
        "tag_4": [None],
        "tag_5": [None],
    })

    result = prepare_book_features(books)

    assert result.loc[0, "content"] == "fantasy magic"