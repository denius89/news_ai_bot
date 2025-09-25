from bs4 import BeautifulSoup
from utils.clean_text import clean_text, extract_text


def test_clean_text_removes_html_tags():
    html = "<p>Hello <b>World</b></p>"
    assert clean_text(html) == "Hello World"


def test_clean_text_normalizes_spaces():
    html = "<div>  Hello   World  </div>"
    assert clean_text(html) == "Hello World"


def test_clean_text_empty_input():
    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_extract_text_from_element():
    el = BeautifulSoup("<span>Value</span>", "html.parser").span
    assert extract_text(el) == "Value"


def test_extract_text_empty():
    assert extract_text(None) is None
    el = BeautifulSoup("<span>   </span>", "html.parser").span
    assert extract_text(el) is None
