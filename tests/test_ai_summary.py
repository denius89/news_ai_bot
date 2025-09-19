from digests.ai_summary import generate_summary

def test_generate_summary_smoke():
    data = [
        {"title": "Биткоин растет", "content": "Цена BTC достигла 70,000$", "source": "crypto"},
        {"title": "Инфляция в США снижается", "content": "Последние данные показали замедление инфляции", "source": "economy"},
    ]
    summary = generate_summary(data, max_tokens=100)
    assert isinstance(summary, str)
    assert len(summary) > 10
