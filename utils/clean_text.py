# utils/clean_text.py
import re
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """Удаляет ВСЕ HTML-теги и нормализует пробелы (для парсинга/анализа)."""
    if not text:
        return ""
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_for_telegram(text: str) -> str:
    """
    Чистит текст, оставляя только разрешённые теги (<b>, <i>, <a>).
    Остальное выбрасывает, чтобы Telegram не падал.
    """
    if not text:
        return ""

    # убираем doctype, html, head, body и прочие неподдерживаемые теги
    text = re.sub(r"(?i)<!doctype.*?>", "", text)
    text = re.sub(r"(?i)<\/?(html|head|body|meta|title|div|span|script).*?>", "", text)

    # оставляем <b>, <i>, <a ...>
    # удаляем атрибуты кроме href
    text = re.sub(r'\s?(class|style|id)=".*?"', "", text)

    # чистим пустые строки
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_text(el):
    """Возвращает текст из BeautifulSoup-элемента или None, если пусто."""
    if not el:
        return None
    text = el.get_text(strip=True)
    return text if text else Noneда
