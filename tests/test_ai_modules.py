import pytest
from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

def test_credibility_range():
    item = {"title": "Bitcoin hits new ATH"}
    score = evaluate_credibility(item)
    assert score is not None, "❌ Credibility вернул None"
    assert isinstance(score, (int, float)), "❌ Credibility должен быть числом"
    assert 0 <= score <= 1, f"❌ Credibility вне диапазона [0,1]: {score}"

def test_importance_range():
    item = {"title": "Ethereum Merge complete"}
    score = evaluate_importance(item)
    assert score is not None, "❌ Importance вернул None"
    assert isinstance(score, (int, float)), "❌ Importance должен быть числом"
    assert 0 <= score <= 1, f"❌ Importance вне диапазона [0,1]: {score}"
