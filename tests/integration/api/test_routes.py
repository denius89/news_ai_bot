from routes import news_routes


def test_routes_import():
    # Проверка, что модуль импортируется
    assert news_routes is not None
