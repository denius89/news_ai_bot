import os
import logging
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance

# --- ЛОГИРОВАНИЕ ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("❌ Не найдены SUPABASE_URL или SUPABASE_KEY в .env")

supabase = create_client(url, key)


# --- Маппинг стран для флагов ---
COUNTRY_MAP = {
    # Северная Америка
    "united states": "us", "us": "us", "u.s.": "us", "usa": "us",
    "canada": "ca", "ca": "ca",
    "mexico": "mx", "mx": "mx",

    # Южная Америка
    "brazil": "br", "br": "br",
    "argentina": "ar", "ar": "ar",
    "chile": "cl", "cl": "cl",

    # Европа
    "united kingdom": "gb", "uk": "gb", "gb": "gb", "england": "gb", "britain": "gb",
    "euro zone": "eu", "euro area": "eu", "eu": "eu",
    "germany": "de", "de": "de",
    "france": "fr", "fr": "fr",
    "italy": "it", "it": "it",
    "spain": "es", "es": "es",
    "portugal": "pt", "pt": "pt",
    "netherlands": "nl", "holland": "nl", "nl": "nl",
    "belgium": "be", "be": "be",
    "switzerland": "ch", "ch": "ch",
    "sweden": "se", "se": "se",
    "norway": "no", "no": "no",
    "denmark": "dk", "dk": "dk",
    "finland": "fi", "fi": "fi",
    "austria": "at", "at": "at",
    "greece": "gr", "gr": "gr",
    "ireland": "ie", "ie": "ie",
    "poland": "pl", "pl": "pl",
    "czech republic": "cz", "czechia": "cz", "cz": "cz",
    "hungary": "hu", "hu": "hu",
    "romania": "ro", "ro": "ro",
    "slovakia": "sk", "sk": "sk",
    "slovenia": "si", "si": "si",

    # Азия
    "china": "cn", "cn": "cn",
    "japan": "jp", "jp": "jp",
    "india": "in", "in": "in",
    "hong kong": "hk", "hk": "hk",
    "singapore": "sg", "sg": "sg",
    "south korea": "kr", "korea": "kr", "republic of korea": "kr", "kr": "kr",
    "taiwan": "tw", "tw": "tw",
    "indonesia": "id", "id": "id",
    "malaysia": "my", "my": "my",
    "thailand": "th", "th": "th",
    "philippines": "ph", "ph": "ph",

    # Океания
    "australia": "au", "au": "au",
    "new zealand": "nz", "nz": "nz",

    # Африка
    "south africa": "za", "za": "za",
    "egypt": "eg", "eg": "eg",
    "nigeria": "ng", "ng": "ng",

    # Ближний Восток
    "israel": "il", "il": "il",
    "turkey": "tr", "tr": "tr",
    "saudi arabia": "sa", "sa": "sa",
    "uae": "ae", "united arab emirates": "ae", "ae": "ae",
    "qatar": "qa", "qa": "qa",
    "kuwait": "kw", "kw": "kw",

    # fallback
    "": None,
}


def upsert_news(item: dict):
    """Добавляет или обновляет новость в базе."""

    link = item.get("link")
    if not link:
        logging.warning("Пропущена новость без ссылки")
        return

    # --- ДАТА ---
    published = item.get("published")
    if isinstance(published, datetime):
        published = published.isoformat()
    if not published:
        published = datetime.now(timezone.utc).isoformat()

    # --- КОНТЕНТ ---
    content = item.get("content") or item.get("title") or ""

    # --- AI ОЦЕНКИ ---
    credibility = evaluate_credibility(item)
    if credibility is None:
        credibility = 0.5

    importance = evaluate_importance(item)
    if importance is None:
        importance = 0.5

    # --- ДАННЫЕ ДЛЯ БАЗЫ ---
    data = {
        "title": item.get("title") or "",
        "link": link,
        "published_at": published,
        "content": content,
        "credibility": credibility,
        "importance": importance,
        "source": item.get("source") or "all",
        "category": item.get("category") or None
    }

    try:
        supabase.table("news").upsert(data, on_conflict=["link"]).execute()
        logging.info(f"✅ Добавлена/обновлена новость: {data['title'][:60]}...")
    except Exception as e:
        logging.error(f"❌ Ошибка при вставке новости: {e}")


def upsert_event(ev: dict) -> None:
    """
    Upsert события по уникальной паре (event_time, title, country).
    Ожидаемые ключи: event_time (datetime|iso str), title, country, currency,
    importance (1..3), fact, forecast, previous.
    """
    event_time = ev.get("event_time")
    if not event_time:
        logging.warning("Пропущено событие без event_time")
        return

    # Нормализация времени в ISO (UTC)
    if isinstance(event_time, datetime):
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        event_time_iso = event_time.astimezone(timezone.utc).isoformat()
    else:
        try:
            dt = datetime.fromisoformat(str(event_time).replace("Z", "+00:00"))
        except Exception:
            try:
                import dateutil.parser
                dt = dateutil.parser.parse(str(event_time))
            except Exception:
                logging.warning(f"Невозможно распарсить event_time: {event_time}")
                return
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        event_time_iso = dt.astimezone(timezone.utc).isoformat()

    # нормализация страны
    raw_country = (ev.get("country") or "").strip().lower()
    raw_currency = (ev.get("currency") or "").strip().lower()

    code = COUNTRY_MAP.get(raw_country)
    if not code and raw_currency:
        code = COUNTRY_MAP.get(raw_currency)

    payload = {
        "event_time": event_time_iso,
        "country": norm,            # человекочитаемое название
        "country_code": code,       # ISO-код для флагов
        "currency": ev.get("currency"),
        "title": ev.get("title") or "",
        "importance": ev.get("importance"),
        "fact": ev.get("fact"),
        "forecast": ev.get("forecast"),
        "previous": ev.get("previous"),
    }

    try:
        # Проверка на существующее событие
        existing = (
            supabase.table("events")
            .select("id")
            .eq("event_time", event_time_iso)
            .eq("title", payload["title"])
            .eq("country", payload["country"])
            .limit(1)
            .execute()
        )
        if existing.data:
            ev_id = existing.data[0]["id"]
            supabase.table("events").update(payload).eq("id", ev_id).execute()
        else:
            supabase.table("events").insert(payload).execute()

        logging.info(f"✅ Upsert event: {payload['title'][:80]} @ {event_time_iso}")
    except Exception as e:
        logging.error(f"❌ Ошибка upsert_event: {e}")