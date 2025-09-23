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

supabase = None
if url and key:
    supabase = create_client(url, key)
else:
    print("⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД.")

# --- Маппинг стран для флагов ---
COUNTRY_MAP = {
    "united states": "us", "us": "us", "u.s.": "us", "usa": "us",
    "canada": "ca", "ca": "ca",
    "mexico": "mx", "mx": "mx",
    "brazil": "br", "br": "br",
    "argentina": "ar", "ar": "ar",
    "chile": "cl", "cl": "cl",
    "united kingdom": "gb", "uk": "gb", "gb": "gb", "england": "gb", "britain": "gb",
    "euro zone": "eu", "euro area": "eu", "eu": "eu",
    "germany": "de", "france": "fr", "italy": "it", "spain": "es",
    "portugal": "pt", "netherlands": "nl", "holland": "nl", "belgium": "be",
    "switzerland": "ch", "sweden": "se", "norway": "no", "denmark": "dk",
    "finland": "fi", "austria": "at", "greece": "gr", "ireland": "ie",
    "poland": "pl", "czech republic": "cz", "czechia": "cz", "hungary": "hu",
    "romania": "ro", "slovakia": "sk", "slovenia": "si",
    "china": "cn", "japan": "jp", "india": "in", "hong kong": "hk",
    "singapore": "sg", "south korea": "kr", "korea": "kr", "republic of korea": "kr",
    "taiwan": "tw", "indonesia": "id", "malaysia": "my", "thailand": "th", "philippines": "ph",
    "australia": "au", "new zealand": "nz",
    "south africa": "za", "egypt": "eg", "nigeria": "ng",
    "israel": "il", "turkey": "tr", "saudi arabia": "sa",
    "uae": "ae", "united arab emirates": "ae", "qatar": "qa", "kuwait": "kw",
    "": None,
}


def upsert_news(item: dict | list[dict]):
    """Добавляет или обновляет новость (или список новостей) в базе."""
    if not supabase:
        logging.warning("⚠️ Supabase не инициализирован, новость не сохранена.")
        return

    # если передан список — рекурсивно обрабатываем каждую новость
    if isinstance(item, list):
        for i in item:
            upsert_news(i)
        return

    link = item.get("link")
    if not link:
        logging.warning("Пропущена новость без ссылки")
        return

    published = item.get("published")
    if isinstance(published, datetime):
        published = published.isoformat()
    if not published:
        published = datetime.now(timezone.utc).isoformat()

    content = item.get("content") or item.get("title") or ""

    credibility = evaluate_credibility(item) or 0.5
    importance = evaluate_importance(item) or 0.5

    data = {
        "title": item.get("title") or "",
        "link": link,
        "published_at": published,
        "content": content,
        "credibility": credibility,
        "importance": importance,
        "source": item.get("source") or "all",
        "category": item.get("category") or None,
    }

    try:
        supabase.table("news").upsert(data, on_conflict=["link"]).execute()
        logging.info(f"✅ Добавлена/обновлена новость: {data['title'][:60]}...")
    except Exception as e:
        logging.error(f"❌ Ошибка при вставке новости: {e}")


def upsert_event(ev: dict) -> None:
    """Добавляет или обновляет событие в базе."""
    if not supabase:
        logging.warning("⚠️ Supabase не инициализирован, событие не сохранено.")
        return

    event_time = ev.get("event_time")
    if not event_time:
        logging.warning("Пропущено событие без event_time")
        return

    # нормализация времени
    if isinstance(event_time, datetime):
        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)
        event_time_iso = event_time.astimezone(timezone.utc).isoformat()
    else:
        try:
            dt = datetime.fromisoformat(str(event_time).replace("Z", "+00:00"))
        except Exception:
            import dateutil.parser
            dt = dateutil.parser.parse(str(event_time))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        event_time_iso = dt.astimezone(timezone.utc).isoformat()

    raw_country = (ev.get("country") or "").strip().lower()
    raw_currency = (ev.get("currency") or "").strip().lower()
    code = COUNTRY_MAP.get(raw_country) or COUNTRY_MAP.get(raw_currency)

    payload = {
        "event_time": event_time_iso,
        "country": raw_country.title() or None,
        "country_code": code,
        "currency": ev.get("currency"),
        "title": ev.get("title") or "",
        "importance": ev.get("importance"),
        "fact": ev.get("fact"),
        "forecast": ev.get("forecast"),
        "previous": ev.get("previous"),
    }

    try:
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