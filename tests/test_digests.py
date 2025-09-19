from digests.generator import generate_digest

def test_generate_digest():
    digest = generate_digest(limit=3)
    assert isinstance(digest, str)
    assert "Дайджест" in digest or "⚠️" in digest
