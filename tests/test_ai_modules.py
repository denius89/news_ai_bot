"""
Тесты для AI-модулей credibility и importance.
"""

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance


def test_credibility_basic():
    """Проверка: функция возвращает float в диапазоне [0, 1]."""
    item = {"title": "Test news"}
    score = evaluate_credibility(item)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_importance_basic():
    """Проверка: функция возвращает float в диапазоне [0, 1]."""
    item = {"title": "Test news"}
    score = evaluate_importance(item)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
