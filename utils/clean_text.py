# utils/clean_text.py
import re
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    """Удаляет HTML-теги и нормализует пробелы (для строк)."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_text(el):
    """Возвращает текст из BeautifulSoup-элемента или None, если пусто (для DOM-элементов)."""
    if not el:
        return None
    text = el.get_text(strip=True)
    return text if text else None