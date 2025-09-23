from digests.generator import generate_digest

def test_generate_digest():
    digest = generate_digest(limit=3)
    assert isinstance(digest, str)
    # допускаем 2 сценария: digest с новостями или fallback без базы
    assert (
        "Дайджест" in digest
        or "⚠️" in digest
        or "Сегодня новостей нет" in digest
    )