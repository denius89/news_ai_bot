import pytest
from bs4 import BeautifulSoup
from parsers.events_parser import fetch_investing_events, IMPORTANCE_TO_PRIORITY, parse_importance


@pytest.mark.integration
def test_fetch_investing_events_smoke():
    """Интеграционный тест: парсер событий Investing.com"""
    events = fetch_investing_events(limit_days=1)

    if not events:
        pytest.skip("❌ Парсер не вернул событий (нет доступа к Investing.com?)")

    # Должен вернуться список словарей
    assert isinstance(events, list)
    assert len(events) > 0

    sample = events[0]
    required_keys = {
        "event_id",
        "title",
        "country",
        "datetime",
        "importance",
        "priority",
        "source",
    }
    for key in required_keys:
        assert key in sample, f"Нет обязательного поля {key}"

    # Проверяем согласованность importance/priority
    importance = sample["importance"]
    priority = sample["priority"]
    assert importance in IMPORTANCE_TO_PRIORITY
    assert priority == IMPORTANCE_TO_PRIORITY[importance]


def test_parse_importance_with_mock_html():
    """Юнит-тест: парсинг важности из mock HTML"""
    html = """
    <td class="sentiment">
        <i class="icon-gray-full-bullish"></i>
        <i class="icon-gray-full-bullish"></i>
        <i class="icon-gray-full-bullish"></i>
    </td>
    """
    cell = BeautifulSoup(html, "html.parser").find("td")
    importance, priority = parse_importance(cell)
    assert importance == 3
    assert priority == "high"

    html = """<td class="sentiment"><i class="icon-gray-full-bullish"></i></td>"""
    cell = BeautifulSoup(html, "html.parser").find("td")
    importance, priority = parse_importance(cell)
    assert importance == 1
    assert priority == "low"

    html = """<td class="sentiment"></td>"""
    cell = BeautifulSoup(html, "html.parser").find("td")
    importance, priority = parse_importance(cell)
    assert importance == 1
    assert priority == "low"
