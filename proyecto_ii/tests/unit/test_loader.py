from book_recommender.loader import load_data

def test_load_data():
    datos = load_data()

    assert set(datos.keys()) == {
        "books",
        "ratings",
        "book_tags",
        "tags",
        "to_read",
    }

    for df in datos.values():
        assert not df.empty
        assert len(df.columns) > 0
