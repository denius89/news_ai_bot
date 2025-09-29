import re
import html
from bs4 import BeautifulSoup


def clean_text(text: str) -> str:
    """Удаляет ВСЕ HTML-теги и нормализует пробелы (plain text)."""
    if not text:
        return ""
    text = html.unescape(text)  # преобразуем HTML-сущности (&nbsp;, &amp; и т.д.)
    text = BeautifulSoup(text, "html.parser").get_text()
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_for_telegram(text: str) -> str:
    """
    Чистит текст под Telegram:
    - убирает <!doctype> и неподдерживаемые контейнеры (<html>, <head>, <meta>, <script>, ...)
    - удаляет вместе с содержимым: <table>, <tr>, <td>, <th>, <img>, <video>, <iframe>
    - заменяет заголовки на <b>
    - превращает параграфы и <br> в переносы строк
    - превращает списки <li> в буллеты
    - оставляет только <b>, <i>, <a href="">
    """
    if not text:
        return ""

    # убираем <!doctype> до парсинга
    text = re.sub(r"(?i)<!doctype.*?>", "", text)
    text = html.unescape(text)

    soup = BeautifulSoup(text, "html.parser")

    # Полностью удаляем таблицы и медиа
    for tag in soup.find_all(["table", "tr", "td", "th", "img", "video", "iframe"]):
        tag.decompose()

    # Заголовки → <b>
    for tag in soup.find_all(re.compile(r"h[1-6]", re.I)):
        tag.name = "b"

    # Параграфы и переносы
    for tag in soup.find_all(["p", "br"]):
        tag.insert_before("\n")
        tag.unwrap()

    # Списки
    for li in soup.find_all("li"):
        li.insert_before("• ")
        li.insert_after("\n")
        li.unwrap()
    for tag in soup.find_all(["ul", "ol"]):
        tag.unwrap()

    # Удаляем ненужные контейнеры
    for tag in soup.find_all(["html", "head", "body", "meta", "title", "div", "span", "script"]):
        tag.unwrap()

    # Чистим атрибуты, кроме href у <a>
    for tag in soup.find_all(True):
        if tag.name == "a":
            href = tag.get("href")
            tag.attrs = {"href": href} if href else {}
        else:
            tag.attrs = {}

    cleaned = str(soup)

    # Убираем лишние пустые строки
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned.strip()


def extract_text(el):
    """Возвращает текст из BeautifulSoup-элемента или None, если пусто."""
    if not el:
        return None
    text = el.get_text(strip=True)
    return text if text else None
