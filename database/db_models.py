import hashlib
import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional, Union
from pathlib import Path
import httpx
from dotenv import load_dotenv
from supabase import create_client, Client

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from config.settings import COUNTRY_MAP
from utils.dates import format_datetime, ensure_utc_iso

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("database")

# --- ПОДКЛЮЧЕНИЕ К SUPABASE ---
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.error("❌ Ошибка инициализации Supabase: %s", e)
else:
    logger.warning("⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД.")


# --- SAFE EXECUTE (ретраи) ---
def safe_execute(query, retries: int = 3, delay: int = 2):
    """
    Выполняет запрос с ретраями при сетевых ошибках Supabase/httpx.
    """
    for attempt in range(1, retries + 1):
        try:
            return query.execute()
        except (httpx.RemoteProtocolError, httpx.ConnectError) as e:
            logger.warning("⚠️ Попытка %s/%s: ошибка соединения %s", attempt, retries, e)
            if attempt < retries:
                time.sleep(delay)
            else:
                raise


# --- UID для новостей ---
def make_uid(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()


# --- Event ID для событий ---
def make_event_id(title: str, country: str, event_time: str) -> str:
    raw = f"{title}|{country}|{event_time}"
    return hashlib.sha256(raw.encode()).hexdigest()


# --- Парсинг дат ---
def parse_datetime_from_row(value: Union[str, datetime, None]) -> Optional[datetime]:
    """
    Парсит значение даты из строки БД в datetime объект.

    Args:
        value: Значение из БД (строка или datetime)

    Returns:
        datetime объект или None
    """
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        try:
            # Попробуем ISO формат
            if "T" in value or "+" in value or value.endswith("Z"):
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            # Попробуем простой формат даты
            elif len(value) == 10 and value.count("-") == 2:
                return datetime.fromisoformat(value + "T00:00:00+00:00")
            # Fallback к текущему времени
            else:
                logger.warning(f"Не удалось распарсить дату: {value}")
                return datetime.now(timezone.utc)
        except Exception as e:
            logger.warning(f"Ошибка парсинга даты '{value}': {e}")
            return datetime.now(timezone.utc)

    return None


# --- Обогащение новостей AI ---
def enrich_news_with_ai(news_item: Dict) -> Dict:
    """Обновляет credibility и importance для новости через AI-модули."""
    # Проверяем, что news_item - это словарь
    if not isinstance(news_item, dict):
        logger.error(f"enrich_news_with_ai получил не словарь: {type(news_item)} = {news_item}")
        # Возвращаем пустой словарь или исходный объект как словарь
        if isinstance(news_item, str):
            return {"content": news_item, "credibility": 0.5, "importance": 0.5}
        return {"credibility": 0.5, "importance": 0.5}

    try:
        news_item["credibility"] = evaluate_credibility(news_item)
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации credibility: {e}")
        news_item["credibility"] = 0.5

    try:
        news_item["importance"] = evaluate_importance(news_item)
    except Exception as e:
        logger.warning(f"Ошибка при AI-аннотации importance: {e}")
        news_item["importance"] = 0.5

    return news_item


# --- UPSERT новостей ---
def upsert_news(items: List[Dict]):
    """Вставляет новости в Supabase без дублей (по uid) и с обогащением AI."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, данные не будут сохранены.")
        return

    rows: List[Dict] = []
    for item in items:
        try:
            # Проверяем, что item - это словарь
            if not isinstance(item, dict):
                logger.error(f"upsert_news получил не словарь: {type(item)} = {item}")
                continue

            enriched = enrich_news_with_ai(item)

            title = (enriched.get("title") or "").strip() or enriched.get("source") or "Без названия"
            content = (enriched.get("content") or "").strip() or (enriched.get("summary") or "").strip() or title
            uid = make_uid(enriched.get("url", ""), title)

            row = {
                "uid": uid,
                "title": title[:512],
                "content": content,
                "link": enriched.get("url"),
                "published_at": ensure_utc_iso(enriched.get("published_at")) or datetime.now(timezone.utc).isoformat(),
                "source": enriched.get("source"),
                "category": (enriched.get("category") or "").lower() or None,
                "credibility": enriched.get("credibility"),
                "importance": enriched.get("importance"),
            }
            logger.debug("Prepared news row: %s", row)
            rows.append(row)
        except Exception as e:
            logger.error("Ошибка подготовки новости: %s, item=%s", e, item)

    if not rows:
        logger.info("Нет новостей для вставки")
        return

    try:
        res = safe_execute(supabase.table("news").upsert(rows, on_conflict="uid"))
        inserted = len(res.data or [])
        logger.info("✅ Upsert news: %s prepared, %s inserted/updated", len(rows), inserted)
        return res
    except Exception as e:
        logger.error("Ошибка при вставке новостей в Supabase: %s", e)


# --- UPSERT событий ---
def upsert_event(items: List[Dict]):
    """Вставляет события в Supabase без дублей (по event_id)."""
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, события не будут сохранены.")
        return

    rows: List[Dict] = []
    for item in items:
        try:
            event_time = item.get("datetime")
            if isinstance(event_time, datetime):
                event_time = ensure_utc_iso(event_time)
            elif not event_time:
                event_time = datetime.now(timezone.utc).isoformat()

            country_raw = (item.get("country") or "").lower()
            country_code = COUNTRY_MAP.get(country_raw)
            event_id = make_event_id(item.get("title", ""), item.get("country", ""), event_time)

            row = {
                "event_id": event_id,
                "event_time": event_time,
                "country": item.get("country"),
                "currency": item.get("currency"),
                "title": item.get("title"),
                "importance": item.get("importance"),
                "priority": item.get("priority"),
                "fact": item.get("fact"),
                "forecast": item.get("forecast"),
                "previous": item.get("previous"),
                "source": item.get("source", "investing"),
                "country_code": country_code,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            logger.debug("Prepared event row: %s", row)
            rows.append(row)
        except Exception as e:
            logger.error("Ошибка подготовки события: %s, item=%s", e, item)

    if not rows:
        logger.info("Нет событий для вставки")
        return

    try:
        res = safe_execute(supabase.table("events").upsert(rows, on_conflict="event_id"))
        inserted = len(res.data or [])
        logger.info("✅ Upsert events: %s prepared, %s inserted/updated", len(rows), inserted)
        return res
    except Exception as e:
        logger.error("Ошибка при вставке событий в Supabase: %s", e)


# 👉 Алиас
upsert_events = upsert_event


# --- Получение событий ---
def get_latest_events(limit: int = 10) -> List[Dict]:
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_events не работает.")
        return []

    query = (
        supabase.table("events")
        .select("event_time, country, country_code, currency, title, importance, fact, forecast, previous, source")
        .order("event_time", desc=False)
        .limit(limit)
    )

    try:
        data = safe_execute(query).data or []
        logger.debug("get_latest_events: fetched %d rows", len(data))
        for ev in data:
            ev["event_time_fmt"] = format_datetime(ev.get("event_time"))
            try:
                ev["importance"] = int(ev.get("importance") or 0)
            except Exception:
                ev["importance"] = 0
        return data
    except Exception as e:
        logger.error("Ошибка при получении событий: %s", e)
        return []


# --- Получение новостей ---
def get_latest_news(
    source: Optional[str] = None,
    categories: Optional[List[str]] = None,
    limit: int = 10,
) -> List[Dict]:
    if not supabase:
        logger.warning("⚠️ Supabase не подключён, get_latest_news не работает.")
        return []

    logger.debug("get_latest_news: source=%s, categories=%s, limit=%s", source, categories, limit)

    query = (
        supabase.table("news")
        .select("id, uid, title, content, link, published_at, source, category, subcategory, credibility, importance")
        .order("published_at", desc=True)
        .limit(limit)
    )

    if source:
        query = query.eq("source", source)
    if categories:
        cats = [c.lower() for c in categories]
        query = query.in_("category", cats)

    try:
        data = safe_execute(query).data or []
        logger.debug("get_latest_news: fetched %d rows", len(data))
        for row in data:
            # Парсим published_at в datetime объект
            row["published_at"] = parse_datetime_from_row(row.get("published_at"))
            # Добавляем форматированную строку для обратной совместимости
            row["published_at_fmt"] = format_datetime(row.get("published_at"))
        return data
    except Exception as e:
        logger.error("Ошибка при получении новостей: %s", e)
        return []


# --- USER MANAGEMENT FUNCTIONS ---


def upsert_user_by_telegram(telegram_id: int, username: str | None = None, locale: str = "ru") -> str:
    """
    Создает или обновляет пользователя по Telegram ID.

    Args:
        telegram_id: Telegram user ID
        username: Telegram username (optional)
        locale: User locale (default: 'ru')

    Returns:
        User ID from database
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return ""

    try:
        # Сначала пытаемся найти существующего пользователя
        existing_user = supabase.table("users").select("id").eq("telegram_id", telegram_id).execute()

        if existing_user.data:
            user_id = existing_user.data[0]["id"]
            logger.debug("Найден существующий пользователь: ID=%s", user_id)
            return user_id

        # Создаем нового пользователя
        new_user = (
            supabase.table("users")
            .insert({"telegram_id": telegram_id, "username": username, "locale": locale})
            .execute()
        )

        if new_user.data:
            user_id = new_user.data[0]["id"]
            logger.info("Создан новый пользователь: ID=%s, telegram_id=%d", user_id, telegram_id)
            return user_id
        else:
            logger.error("Не удалось создать пользователя")
            return ""

    except Exception as e:
        logger.error("Ошибка при создании/поиске пользователя: %s", e)
        return ""


def get_user_by_telegram(telegram_id: int) -> dict | None:
    """
    Получает пользователя по Telegram ID.

    Args:
        telegram_id: Telegram user ID

    Returns:
        User data dict or None if not found
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return None

    try:
        result = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()

        if result.data:
            return result.data[0]
        return None

    except Exception as e:
        logger.error("Ошибка при получении пользователя: %s", e)
        return None


def add_subscription(user_id: str, category: str) -> bool:
    """
    Добавляет подписку на категорию для пользователя.

    Args:
        user_id: User ID
        category: News category

    Returns:
        True if subscription was added, False if already exists
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        result = supabase.table("subscriptions").insert({"user_id": user_id, "category": category}).execute()

        if result.data:
            logger.info("Добавлена подписка: user_id=%d, category=%s", user_id, category)
            return True
        else:
            logger.debug("Подписка уже существует: user_id=%d, category=%s", user_id, category)
            return False

    except Exception as e:
        logger.error("Ошибка при добавлении подписки: %s", e)
        return False


def remove_subscription(user_id: str, category: str) -> int:
    """
    Удаляет подписку на категорию для пользователя.

    Args:
        user_id: User ID
        category: News category

    Returns:
        Number of deleted subscriptions (0 or 1)
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return 0

    try:
        result = supabase.table("subscriptions").delete().eq("user_id", user_id).eq("category", category).execute()

        deleted_count = len(result.data) if result.data else 0
        if deleted_count > 0:
            logger.info("Удалена подписка: user_id=%d, category=%s", user_id, category)

        return deleted_count

    except Exception as e:
        logger.error("Ошибка при удалении подписки: %s", e)
        return 0


def list_subscriptions(user_id: str) -> list[dict]:
    """
    Получает список подписок пользователя.

    Args:
        user_id: User ID

    Returns:
        List of subscription dicts
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        result = supabase.table("subscriptions").select("*").eq("user_id", user_id).execute()

        return result.data or []

    except Exception as e:
        logger.error("Ошибка при получении подписок: %s", e)
        return []


def upsert_notification(
    user_id: str,
    type_: str = "digest",
    frequency: str = "daily",
    enabled: bool = True,
    preferred_hour: int = 9,
) -> None:
    """
    Создает или обновляет настройки уведомлений для пользователя.

    Args:
        user_id: User ID
        type_: Notification type ('digest', 'events', 'breaking')
        frequency: Notification frequency ('daily', 'weekly', 'instant')
        enabled: Whether notification is enabled
        preferred_hour: Preferred hour for daily notifications (0-23)
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return

    try:
        # Используем upsert для создания или обновления
        # Указываем on_conflict для обработки дубликатов по (user_id, type)
        result = (
            supabase.table("notifications")
            .upsert(
                {
                    "user_id": user_id,
                    "type": type_,
                    "frequency": frequency,
                    "enabled": enabled,
                    "preferred_hour": preferred_hour,
                },
                on_conflict="user_id,type",  # Указываем колонки для обработки конфликтов
            )
            .execute()
        )

        if result.data:
            logger.info("Обновлены настройки уведомлений: user_id=%s, type=%s", user_id, type_)

    except Exception as e:
        logger.error("Ошибка при обновлении настроек уведомлений: %s", e)


def list_notifications(user_id: str) -> list[dict]:
    """
    Получает список настроек уведомлений пользователя.

    Args:
        user_id: User ID

    Returns:
        List of notification settings dicts
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        result = supabase.table("notifications").select("*").eq("user_id", user_id).execute()

        return result.data or []

    except Exception as e:
        logger.error("Ошибка при получении настроек уведомлений: %s", e)
        return []


# --- USER NOTIFICATIONS FUNCTIONS ---


def get_user_notifications(user_id: Union[int, str], limit: int = 50, offset: int = 0) -> List[Dict]:
    """
    Получает уведомления пользователя.

    Args:
        user_id: User ID
        limit: Maximum number of notifications to return
        offset: Number of notifications to skip

    Returns:
        List of notification dicts
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        result = (
            supabase.table("user_notifications")
            .select("id, title, message, read, user_id")
            .eq("user_id", user_id)
            .order("id", desc=True)  # Use id instead of created_at
            .limit(limit)
            .execute()
        )

        notifications = result.data or []
        logger.info("Получено уведомлений: %d для user_id=%s", len(notifications), user_id)
        return notifications

    except Exception as e:
        logger.error("Ошибка при получении уведомлений: %s", e)
        return []


def create_user_notification(
    user_id: Union[int, str],
    title: str,
    content: str,
    category: str = "general",
    read: bool = False,
    via_telegram: bool = False,
    via_webapp: bool = True,
) -> Optional[str]:
    """
    Создает новое уведомление для пользователя.

    Args:
        user_id: User ID
        title: Заголовок уведомления
        content: Содержимое уведомления
        category: Категория уведомления
        read: Прочитано ли уведомление
        via_telegram: Отправлять ли через Telegram
        via_webapp: Показывать ли в WebApp

    Returns:
        ID созданного уведомления или None в случае ошибки
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return None

    try:
        notification_data = {
            "user_id": str(user_id),
            "title": title,
            "message": content,  # В базе поле называется message
            "category": category,
            "read": read,
            "via_telegram": via_telegram,
            "via_webapp": via_webapp,
        }

        result = supabase.table("user_notifications").insert(notification_data).execute()

        if result.data and len(result.data) > 0:
            notification_id = result.data[0].get("id")
            logger.info(f"✅ Создано уведомление: user_id={user_id}, notification_id={notification_id}")
            return str(notification_id)
        else:
            logger.error(f"❌ Не удалось создать уведомление для user_id={user_id}")
            return None

    except Exception as e:
        logger.error(f"❌ Ошибка при создании уведомления: {e}")
        return None


def mark_notification_read(user_id: Union[int, str], notification_id: Union[int, str]) -> bool:
    """
    Отмечает уведомление как прочитанное.

    Args:
        user_id: User ID
        notification_id: Notification ID

    Returns:
        True if notification was marked as read, False otherwise
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        logger.info("Marking notification as read: user_id=%s, notification_id=%s", user_id, notification_id)
        result = (
            supabase.table("user_notifications")
            .update({"read": True})
            .eq("id", notification_id)
            .eq("user_id", user_id)  # Безопасность: только свои уведомления
            .execute()
        )
        logger.info("Update result: %s", result.data)

        if result.data and len(result.data) > 0:
            logger.info(
                "Уведомление отмечено как прочитанное: user_id=%s, notification_id=%s",
                user_id,
                notification_id,
            )
            return True
        else:
            logger.warning(
                "Уведомление не найдено или не принадлежит пользователю: user_id=%s, notification_id=%s",
                user_id,
                notification_id,
            )
            return False

    except Exception as e:
        logger.error("Ошибка при отметке уведомления как прочитанного: %s", e)
        return False
