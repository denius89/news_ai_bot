import pytest
from bs4 import BeautifulSoup
from utils.text.clean_text import clean_text, extract_text, clean_for_telegram

# ✅ Все тесты в этом файле — unit
pytestmark = pytest.mark.unit


# --- Тесты для clean_text ---
def test_clean_text_removes_html_tags():
    html = "<p>Hello <b>World</b></p>"
    cleaned = clean_text(html)
    assert cleaned == "Hello World"


def test_clean_text_normalizes_spaces():
    html = "<div>  Hello   World  </div>"
    cleaned = clean_text(html)
    assert cleaned == "Hello World"


def test_clean_text_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""


# --- Тесты для extract_text ---
def test_extract_text_from_element():
    el = BeautifulSoup("<span>Value</span>", "html.parser").span
    assert extract_text(el) == "Value"


def test_extract_text_empty_or_whitespace():
    assert extract_text(None) is None
    el = BeautifulSoup("<span>   </span>", "html.parser").span
    assert extract_text(el) is None


# --- Тесты для clean_for_telegram ---
def test_clean_for_telegram_removes_doctype_and_html():
    raw = "<!doctype html><html><body><h2>Title</h2><p>Text</p></body></html>"
    cleaned = clean_for_telegram(raw)

    assert "<!doctype" not in cleaned.lower()
    assert "<html" not in cleaned.lower()
    assert "<body" not in cleaned.lower()
    assert "<b>Title</b>" in cleaned  # <h2> → <b>
    assert "Text" in cleaned


def test_clean_for_telegram_paragraphs_and_breaks():
    raw = "<p>First</p><br><p>Second</p>"
    cleaned = clean_for_telegram(raw)

    assert "First" in cleaned
    assert "Second" in cleaned
    assert "\n" in cleaned  # переносы сохранены


def test_clean_for_telegram_lists_are_bulleted():
    raw = "<ul><li>Item 1</li><li>Item 2</li></ul>"
    cleaned = clean_for_telegram(raw)

    assert "• Item 1" in cleaned
    assert "• Item 2" in cleaned
    assert "<li>" not in cleaned
    assert "<ul>" not in cleaned
    assert "<ol>" not in cleaned


def test_clean_for_telegram_removes_tables_and_media_but_keeps_text():
    raw = "<table><tr><td>Cell</td></tr></table><img src='x.png'>Video<iframe></iframe>"
    cleaned = clean_for_telegram(raw)

    assert "Cell" not in cleaned  # содержимое таблицы удалено
    assert "<table>" not in cleaned
    assert "<td>" not in cleaned
    assert "img" not in cleaned
    assert "iframe" not in cleaned
    assert "Video" in cleaned  # обычный текст "Video" остаётся


def test_clean_for_telegram_keeps_supported_tags():
    raw = '<b>bold</b> <i>italic</i> <a href="http://test">link</a>'
    cleaned = clean_for_telegram(raw)

    assert "<b>bold</b>" in cleaned
    assert "<i>italic</i>" in cleaned
    assert '<a href="http://test">link</a>' in cleaned
