"""
Module: database.db_models
Purpose: Core database operations and Supabase client management (Legacy)
Location: database/db_models.py

Description:
    Legacy модуль для работы с базой данных через Supabase.
    Предоставляет функции для CRUD операций с новостями, событиями,
    пользователями, дайджестами и аналитикой.

    ⚠️ ВАЖНО: Это legacy модуль. Для нового кода используйте database.service

Key Components:
    - supabase: Глобальный синхронный Supabase клиент
    - safe_execute(): Retry wrapper для database queries
    - News operations: upsert_news(), get_latest_news()
    - Events operations: upsert_event(), get_latest_events()
    - User management: upsert_user_by_telegram(), get_user_by_telegram()
    - Digest operations: save_digest(), get_user_digests()
    - Analytics: log_digest_generation(), get_digest_analytics()

Dependencies:
    External:
        - supabase-py: Supabase Python client
        - python-dotenv: Environment variables
    Internal:
        - ai_modules.credibility: Credibility scoring
        - ai_modules.importance: Importance scoring
        - config.core.settings: Configuration
        - utils.system.dates: Date utilities

Usage Example:
    ```python
    from database.db_models import get_latest_news, upsert_news

    # Получить последние новости
    news = get_latest_news(categories=["tech", "crypto"], limit=10)

    # Вставить новости
    news_items = [{"title": "...", "content": "...", ...}]
    upsert_news(news_items)
    ```

Migration Path:
    Старый код использует этот модуль (22 файла зависят от него).
    Постепенно мигрируем на database.service:

    ```python
    # Старый способ (db_models):
    from database.db_models import get_latest_news
    news = get_latest_news(limit=10)

    # Новый способ (service):
    from database.service import get_sync_service
    db_service = get_sync_service()
    news = db_service.get_latest_news(limit=10)
    ```

Notes:
    - Загружает .env из config_files/.env (не из settings!)
    - Использует глобальное состояние (global supabase client)
    - Смешивает разные домены (news, events, users, digests)
    - HTTP/2 отключен для избежания pseudo-header errors
    - Не рекомендуется для нового кода

Author: PulseAI Team
Last Updated: October 2025
"""

import hashlib
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional, Union
from supabase import create_client, Client

from ai_modules.credibility import evaluate_credibility
from ai_modules.importance import evaluate_importance
from config.core.settings import COUNTRY_MAP, SUPABASE_URL, SUPABASE_KEY
from utils.system.dates import format_datetime, ensure_utc_iso

# --- ЛОГИРОВАНИЕ ---
logger = logging.getLogger("database")

supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        # Принудительно отключаем HTTP/2 для решения pseudo-header ошибки
        os.environ["HTTPX_NO_HTTP2"] = "1"
        os.environ["SUPABASE_HTTP2_DISABLED"] = "1"

        # Стандартная инициализация с отключенным HTTP/2
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized with HTTP/2 disabled via environment")
    except Exception as e:
        logger.error("❌ Ошибка инициализации Supabase: %s", e)
else:
    logger.warning("⚠️ Supabase не инициализирован (нет ключей). Unit-тесты будут выполняться без БД.")


# --- SAFE EXECUTE (ретраи) ---
def safe_execute(query, retries: int = 5, delay: float = 1.0):
    """
    Выполняет запрос с ретраями при сетевых ошибках Supabase/httpx.
    Увеличено количество попыток и добавлена экспоненциальная задержка.
    """
    for attempt in range(1, retries + 1):
        try:
            logger.info(f"🔍 Database query attempt {attempt}/{retries}")
            result = query.execute()
            logger.info(f"✅ Database query successful on attempt {attempt}")
            return result
        except Exception as e:
            error_str = str(e)
            if "ConnectionTerminated" in error_str or "error_code:9" in error_str:
                logger.warning(f"⚠️ HTTP/2 connection error attempt {attempt}/{retries}: {e}")
            else:
                logger.warning(f"⚠️ Database error attempt {attempt}/{retries}: {e}")

            if attempt < retries:
                # Экспоненциальная задержка: 1s, 2s, 4s, 8s
                wait_time = delay * (2 ** (attempt - 1))
                logger.info(f"⏳ Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"❌ Query failed after {retries} attempts: {e}")
                raise


# --- UID для новостей ---
def make_uid(url: str, title: str) -> str:
    return hashlib.sha256(f"{url}|{title}".encode()).hexdigest()


# --- Event ID для событий ---
def make_event_id(title: str, country: str, event_time: str) -> str:
    raw = f"{title}|{country}|{event_time}"
    return hashlib.sha256(raw.encode()).hexdigest()


# --- Парсинг дат ---
def parse_datetime_from_row(
    value: Union[str, datetime, None],
) -> Optional[datetime]:
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
            return {
                "content": news_item,
                "credibility": 0.5,
                "importance": 0.5,
            }
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
        logger.info(
            "✅ Upsert news: %s prepared, %s inserted/updated",
            len(rows),
            inserted,
        )
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
        logger.info(
            "✅ Upsert events: %s prepared, %s inserted/updated",
            len(rows),
            inserted,
        )
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

    logger.debug(
        "get_latest_news: source=%s, categories=%s, limit=%s",
        source,
        categories,
        limit,
    )

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


def upsert_user_by_telegram(
    telegram_id: int,
    username: str | None = None,
    locale: str = "ru",
    first_name: str | None = None,
) -> str:
    """
    Создает или обновляет пользователя по Telegram ID.

    Args:
        telegram_id: Telegram user ID
        username: Telegram username (optional)
        locale: User locale (default: 'ru')
        first_name: User first name (optional)

    Returns:
        User ID from database
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return ""

    try:
        # Импортируем нормализацию имён
        from utils.text.name_normalizer import normalize_user_name

        # Нормализуем имя пользователя
        normalized_first_name = normalize_user_name(first_name, username, telegram_id)

        # Сначала пытаемся найти существующего пользователя
        existing_user = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()

        if existing_user.data:
            user_data = existing_user.data[0]
            user_id = user_data["id"]

            # Проверяем, нужно ли обновить данные пользователя
            update_data = {}
            if normalized_first_name and not user_data.get("first_name"):
                update_data["first_name"] = normalized_first_name
            if username and not user_data.get("username"):
                update_data["username"] = username

            # Обновляем пользователя, если есть новые данные
            if update_data:
                update_data["updated_at"] = "now()"
                supabase.table("users").update(update_data).eq("id", user_id).execute()
                logger.info(
                    "Обновлены данные пользователя: ID=%s, данные=%s",
                    user_id,
                    update_data,
                )

            logger.debug("Найден существующий пользователь: ID=%s", user_id)
            return user_id

        # Создаем нового пользователя с нормализованным именем
        new_user_data = {
            "telegram_id": telegram_id,
            "username": username,
            "locale": locale,
            "first_name": normalized_first_name,
        }

        new_user = supabase.table("users").insert(new_user_data).execute()

        if new_user.data:
            user_id = new_user.data[0]["id"]
            logger.info(
                "Создан новый пользователь: ID=%s, telegram_id=%d, first_name=%s",
                user_id,
                telegram_id,
                first_name,
            )
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
            logger.info(
                "Добавлена подписка: user_id=%d, category=%s",
                user_id,
                category,
            )
            return True
        else:
            logger.debug(
                "Подписка уже существует: user_id=%d, category=%s",
                user_id,
                category,
            )
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
            logger.info(
                "Обновлены настройки уведомлений: user_id=%s, type=%s",
                user_id,
                type_,
            )

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
        logger.info(
            "Получено уведомлений: %d для user_id=%s",
            len(notifications),
            user_id,
        )
        return notifications

    except Exception as e:
        logger.error("Ошибка при получении уведомлений: %s", e)
        return []


def create_user(
    telegram_id: int,
    username: str = None,
    locale: str = "ru",
    first_name: str = None,
) -> str:
    """
    Создает нового пользователя в базе данных.

    Args:
        telegram_id: ID пользователя в Telegram
        username: Имя пользователя (опционально)
        locale: Локаль пользователя (по умолчанию 'ru')
        first_name: Имя пользователя (опционально)

    Returns:
        UUID нового пользователя или пустую строку при ошибке
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return ""

    try:
        import uuid

        # Генерируем новый UUID для пользователя
        new_user_id = str(uuid.uuid4())

        # Создаем пользователя
        result = (
            supabase.table("users")
            .insert(
                {
                    "id": new_user_id,
                    "telegram_id": telegram_id,
                    "username": username,
                    "locale": locale,
                    "first_name": first_name,
                    "created_at": "now()",
                    "updated_at": "now()",
                }
            )
            .execute()
        )

        if result.data:
            logger.info(
                f"Новый пользователь создан: ID={new_user_id}, telegram_id={telegram_id}, first_name={first_name}"
            )
            return new_user_id
        else:
            logger.error("Не удалось создать пользователя")
            return ""

    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        return ""


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
        logger.info(
            "Marking notification as read: user_id=%s, notification_id=%s",
            user_id,
            notification_id,
        )
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


# --- DIGEST FUNCTIONS ---


def save_digest(
    user_id: str,
    summary: str,
    category: str = "all",
    style: str = "analytical",
    period: str = "today",
    limit_count: int = 10,
    metadata: dict = None,
) -> str:
    """
    Сохраняет дайджест в базу данных.

    Args:
        user_id: ID пользователя
        summary: Текст дайджеста
        category: Категория новостей (crypto, sports, markets, tech, world, all)
        style: Стиль генерации (analytical, business, meme)
        period: Период (today, 7d, 30d)
        limit_count: Количество новостей в дайджесте
        metadata: Дополнительные метаданные

    Returns:
        ID созданного дайджеста или пустую строку в случае ошибки
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return ""

    try:
        # Полная версия с новыми колонками после миграции
        digest_data = {
            "user_id": str(user_id),
            "summary": summary,
            "category": category,
            "style": style,
            "period": period,
            "limit_count": limit_count,
            "deleted_at": None,
            "archived": False,
            "metadata": metadata or {},
        }

        result = supabase.table("digests").insert(digest_data).execute()

        if result.data:
            digest_id = result.data[0]["id"]
            logger.info(
                "Дайджест сохранен: ID=%s, user_id=%s, category=%s, style=%s",
                digest_id,
                user_id,
                category,
                style,
            )
            return digest_id
        else:
            logger.error("Не удалось сохранить дайджест")
            return ""

    except Exception as e:
        logger.error("Ошибка при сохранении дайджеста: %s", e)
        return ""


def get_user_digests(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    include_deleted: bool = False,
    include_archived: bool = False,
) -> List[Dict]:
    """
    Получает историю дайджестов пользователя с поддержкой мягкого удаления и архивирования.
    Полная версия с новыми колонками после миграции.

    Args:
        user_id: ID пользователя
        limit: Максимальное количество дайджестов
        offset: Смещение для пагинации
        include_deleted: Включать ли удаленные дайджесты
        include_archived: Включать ли архивированные дайджесты

    Returns:
        Список дайджестов пользователя
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        query = supabase.table("digests").select("*").eq("user_id", user_id)

        # Фильтрация по статусу с новыми колонками
        if include_deleted and include_archived:
            # Все дайджесты (включая удаленные и архивированные)
            pass
        elif include_deleted and not include_archived:
            # Только удаленные (не архивированные)
            query = query.not_.is_("deleted_at", "null")  # deleted = TRUE
            query = query.eq("archived", False)
        elif not include_deleted and include_archived:
            # Только архивированные (не удаленные)
            query = query.is_("deleted_at", "null")  # deleted = FALSE
            query = query.eq("archived", True)
        else:  # not include_deleted and not include_archived
            # Только активные (не удаленные и не архивированные)
            query = query.is_("deleted_at", "null")  # deleted = FALSE
            query = query.eq("archived", False)

        result = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()

        return result.data or []

    except Exception as e:
        logger.error("Ошибка при получении дайджестов пользователя: %s", e)
        return []


def get_digest_by_id(digest_id: str, user_id: str = None) -> Dict:
    """
    Получает дайджест по ID.

    Args:
        digest_id: ID дайджеста
        user_id: ID пользователя (опционально, для проверки принадлежности)

    Returns:
        Данные дайджеста или None если не найден
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return None

    try:
        query = supabase.table("digests").select("*").eq("id", digest_id)

        if user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()

        if result.data:
            return result.data[0]
        else:
            logger.warning("Дайджест не найден: ID=%s", digest_id)
            return None

    except Exception as e:
        logger.error("Ошибка при получении дайджеста: %s", e)
        return None


def soft_delete_digest(digest_id: str, user_id: str) -> bool:
    """
    Мягко удаляет дайджест пользователя (устанавливает deleted_at).

    Args:
        digest_id: ID дайджеста
        user_id: ID пользователя

    Returns:
        True если дайджест удален, False в противном случае
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        from datetime import datetime

        result = (
            supabase.table("digests")
            .update({"deleted_at": datetime.utcnow().isoformat()})
            .eq("id", digest_id)
            .eq("user_id", user_id)
            .is_("deleted_at", "null")  # Только если еще не удален
            .execute()
        )

        if result.data:
            logger.info("Дайджест мягко удален: ID=%s, user_id=%s", digest_id, user_id)
            return True
        else:
            logger.warning(
                "Дайджест не найден, не принадлежит пользователю или уже удален: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return False

    except Exception as e:
        logger.error("Ошибка при мягком удалении дайджеста: %s", e)
        return False


def restore_digest(digest_id: str, user_id: str) -> bool:
    """
    Восстанавливает мягко удаленный дайджест.

    Args:
        digest_id: ID дайджеста
        user_id: ID пользователя

    Returns:
        True если дайджест восстановлен, False в противном случае
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        result = (
            supabase.table("digests")
            .update(
                {
                    "deleted_at": None,
                    "archived": False,  # Также убираем архивирование при восстановлении
                }
            )
            .eq("id", digest_id)
            .eq("user_id", user_id)
            .not_.is_("deleted_at", "null")  # Только если удален (deleted_at IS NOT NULL)
            .execute()
        )

        if result.data:
            logger.info("Дайджест восстановлен: ID=%s, user_id=%s", digest_id, user_id)
            return True
        else:
            logger.warning(
                "Дайджест не найден, не принадлежит пользователю или не удален: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return False

    except Exception as e:
        logger.error("Ошибка при восстановлении дайджеста: %s", e)
        return False


def archive_digest(digest_id: str, user_id: str) -> bool:
    """
    Архивирует дайджест пользователя.

    Args:
        digest_id: ID дайджеста
        user_id: ID пользователя

    Returns:
        True если дайджест архивирован, False в противном случае
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        result = (
            supabase.table("digests")
            .update({"archived": True})
            .eq("id", digest_id)
            .eq("user_id", user_id)
            .eq("archived", False)  # Только если не архивирован
            .is_("deleted_at", "null")  # Только если не удален
            .execute()
        )

        if result.data:
            logger.info("Дайджест архивирован: ID=%s, user_id=%s", digest_id, user_id)
            return True
        else:
            logger.warning(
                "Дайджест не найден, не принадлежит пользователю, уже архивирован или удален: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return False

    except Exception as e:
        logger.error("Ошибка при архивировании дайджеста: %s", e)
        return False


def unarchive_digest(digest_id: str, user_id: str) -> bool:
    """
    Разархивирует дайджест пользователя.

    Args:
        digest_id: ID дайджеста
        user_id: ID пользователя

    Returns:
        True если дайджест разархивирован, False в противном случае
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        result = (
            supabase.table("digests")
            .update(
                {
                    "archived": False,
                    "deleted_at": None,  # Также убираем удаление при разархивировании
                }
            )
            .eq("id", digest_id)
            .eq("user_id", user_id)
            .eq("archived", True)  # Только если архивирован
            .execute()
        )

        if result.data:
            logger.info(
                "Дайджест разархивирован: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return True
        else:
            logger.warning(
                "Дайджест не найден, не принадлежит пользователю или не архивирован: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return False

    except Exception as e:
        logger.error("Ошибка при разархивировании дайджеста: %s", e)
        return False


def permanent_delete_digest(digest_id: str, user_id: str) -> bool:
    """
    Окончательно удаляет дайджест пользователя (физическое удаление).

    Args:
        digest_id: ID дайджеста
        user_id: ID пользователя

    Returns:
        True если дайджест удален, False в противном случае
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        result = supabase.table("digests").delete().eq("id", digest_id).eq("user_id", user_id).execute()

        if result.data:
            logger.info(
                "Дайджест окончательно удален: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return True
        else:
            logger.warning(
                "Дайджест не найден или не принадлежит пользователю: ID=%s, user_id=%s",
                digest_id,
                user_id,
            )
            return False

    except Exception as e:
        logger.error("Ошибка при окончательном удалении дайджеста: %s", e)
        return False


# =============================================================================
# USER PREFERENCES FUNCTIONS
# =============================================================================


def save_user_preferences(
    user_id: str,
    preferred_category: str = "all",
    preferred_style: str = "analytical",
    preferred_period: str = "today",
    min_importance: float = 0.3,
    enable_smart_filtering: bool = True,
) -> bool:
    """
    Сохраняет предпочтения пользователя.

    Args:
        user_id: ID пользователя
        preferred_category: Предпочитаемая категория
        preferred_style: Предпочитаемый стиль
        preferred_period: Предпочитаемый период
        min_importance: Минимальная важность новостей
        enable_smart_filtering: Включить умную фильтрацию

    Returns:
        True если успешно сохранено
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        preferences_data = {
            "user_id": user_id,
            "preferred_category": preferred_category,
            "preferred_style": preferred_style,
            "preferred_period": preferred_period,
            "min_importance": min_importance,
            "enable_smart_filtering": enable_smart_filtering,
            "last_used_at": datetime.now(timezone.utc).isoformat(),
        }

        # Используем upsert для обновления существующих предпочтений
        supabase.table("user_preferences").upsert(preferences_data, on_conflict="user_id").execute()

        logger.info(f"Предпочтения пользователя {user_id} сохранены")
        return True

    except Exception as e:
        logger.error(f"Ошибка при сохранении предпочтений пользователя {user_id}: {e}")
        return False


def get_user_preferences(user_id: str) -> Dict:
    """
    Получает предпочтения пользователя.

    Args:
        user_id: ID пользователя

    Returns:
        Словарь с предпочтениями или значения по умолчанию
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return _get_default_preferences()

    try:
        result = supabase.table("user_preferences").select("*").eq("user_id", user_id).execute()

        if result.data:
            preferences = result.data[0]
            logger.debug(f"Найдены предпочтения для пользователя {user_id}")
            return preferences
        else:
            logger.debug(f"Предпочтения для пользователя {user_id} не найдены, возвращаем по умолчанию")
            return _get_default_preferences()

    except Exception as e:
        logger.error(f"Ошибка при получении предпочтений пользователя {user_id}: {e}")
        return _get_default_preferences()


def _get_default_preferences() -> Dict:
    """Возвращает предпочтения по умолчанию."""
    return {
        "preferred_category": "all",
        "preferred_style": "analytical",
        "preferred_period": "today",
        "min_importance": 0.3,
        "enable_smart_filtering": True,
    }


# =============================================================================
# ANALYTICS FUNCTIONS
# =============================================================================


def log_digest_generation(
    user_id: str,
    category: str,
    style: str,
    period: str,
    min_importance: float = None,
    generation_time_ms: int = None,
    success: bool = True,
    error_message: str = None,
    news_count: int = 0,
) -> bool:
    """
    Логирует генерацию дайджеста для аналитики.

    Args:
        user_id: ID пользователя
        category: Категория дайджеста
        style: Стиль дайджеста
        period: Период дайджеста
        min_importance: Минимальная важность
        generation_time_ms: Время генерации в миллисекундах
        success: Успешность генерации
        error_message: Сообщение об ошибке
        news_count: Количество новостей в дайджесте

    Returns:
        True если успешно залогировано
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        analytics_data = {
            "user_id": user_id,
            "category": category,
            "style": style,
            "period": period,
            "min_importance": min_importance,
            "generation_time_ms": generation_time_ms,
            "success": success,
            "error_message": error_message,
            "news_count": news_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = safe_execute(supabase.table("digest_analytics").insert(analytics_data))

        if result.data:
            logger.debug(f"Аналитика генерации дайджеста залогирована для пользователя {user_id}")
            return True
        else:
            logger.error(f"Не удалось залогировать аналитику для пользователя {user_id}")
            return False

    except Exception as e:
        logger.error(f"Ошибка при логировании аналитики для пользователя {user_id}: {e}")
        return False


def get_digest_analytics(user_id: str = None, days: int = 30) -> List[Dict]:
    """
    Получает аналитику генерации дайджестов.

    Args:
        user_id: ID пользователя (опционально)
        days: Количество дней для анализа

    Returns:
        Список записей аналитики
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        # Вычисляем дату начала периода
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        query = supabase.table("digest_analytics").select("*").gte("created_at", start_date.isoformat())

        if user_id:
            query = query.eq("user_id", user_id)

        result = safe_execute(query.order("created_at", desc=True))

        return result.data or []

    except Exception as e:
        logger.error(f"Ошибка при получении аналитики: {e}")
        return []


# =============================================================================
# SMART FILTERING FUNCTIONS
# =============================================================================


def get_latest_news_with_importance(
    source: str = None,
    categories: List[str] = None,
    limit: int = 10,
    min_importance: float = None,
) -> List[Dict]:
    """
    Получает последние новости с фильтрацией по важности.

    Args:
        source: Источник новостей
        categories: Список категорий
        limit: Максимальное количество новостей
        min_importance: Минимальная важность новостей

    Returns:
        Список новостей, отсортированных по важности
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        query = (
            supabase.table("news")
            .select(
                "id, uid, title, content, link, published_at, source, category, subcategory, credibility, importance"
            )
            .order("published_at", desc=True)
            .limit(limit)
        )

        if source:
            query = query.eq("source", source)

        if categories:
            cats = [c.lower() for c in categories]
            query = query.in_("category", cats)

        if min_importance is not None:
            query = query.gte("importance", min_importance)

        result = query.execute()
        data = result.data or []

        # Сортируем по важности (если не указана min_importance)
        if min_importance is None:
            data = sorted(data, key=lambda x: x.get("importance", 0), reverse=True)

        logger.debug(f"Получено {len(data)} новостей с фильтрацией по важности")

        for row in data:
            # Парсим published_at в datetime объект
            row["published_at"] = parse_datetime_from_row(row.get("published_at"))
            # Добавляем форматированную строку для обратной совместимости
            row["published_at_fmt"] = format_datetime(row.get("published_at"))

        return data

    except Exception as e:
        logger.error(f"Ошибка при получении новостей с фильтрацией: {e}")
        # Fallback на старую функцию
        return get_latest_news(source, categories, limit)


def get_smart_filter_for_time() -> Dict:
    """
    Получает умный фильтр в зависимости от времени дня.

    Returns:
        Словарь с параметрами фильтра
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return _get_default_smart_filter()

    try:
        current_hour = datetime.now().hour
        current_weekday = datetime.now().weekday()

        # Определяем условие времени
        if current_weekday >= 5:  # Выходные
            time_condition = "weekend"
        elif 6 <= current_hour < 12:  # Утро
            time_condition = "morning"
        elif 18 <= current_hour < 23:  # Вечер
            time_condition = "evening"
        else:
            time_condition = "all"

        result = (
            supabase.table("smart_filters")
            .select("*")
            .eq("time_condition", time_condition)
            .eq("is_active", True)
            .execute()
        )

        if result.data:
            filter_data = result.data[0]
            logger.debug(f"Применен умный фильтр для времени: {time_condition}")
            return filter_data
        else:
            logger.debug(f"Умный фильтр для времени {time_condition} не найден, используем по умолчанию")
            return _get_default_smart_filter()

    except Exception as e:
        logger.error(f"Ошибка при получении умного фильтра: {e}")
        return _get_default_smart_filter()


def _get_default_smart_filter() -> Dict:
    """Возвращает умный фильтр по умолчанию."""
    return {
        "min_importance": 0.3,
        "max_items": 10,
        "categories": None,
        "time_condition": "all",
    }


# =========================
# DIGEST METRICS FUNCTIONS
# =========================


def save_digest_with_metrics(
    user_id: str,
    summary: str,
    category: str,
    style: str,
    confidence: float,
    generation_time_sec: float,
    meta: dict,
    skipped_reason: Optional[str] = None,
) -> str:
    """
    Save digest with metrics to database.

    Args:
        user_id: User ID
        summary: Digest content
        category: News category
        style: AI style (analytical, business, meme)
        confidence: AI confidence score (0.0-1.0)
        generation_time_sec: Time taken to generate digest
        meta: Additional metadata (style_profile, tone, length, audience)
        skipped_reason: Reason why digest was skipped (if any)

    Returns:
        Digest ID
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return None

    try:
        digest_data = {
            "user_id": user_id,
            "summary": summary,
            "category": category,
            "style": style,
            "confidence": confidence,
            "generation_time_sec": generation_time_sec,
            "meta": meta,
            "skipped_reason": skipped_reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        result = safe_execute(supabase.table("digests").insert(digest_data))

        if result.data:
            digest_id = result.data[0]["id"]
            logger.info(f"✅ Digest saved with metrics: {digest_id}")

            # Update daily analytics
            # update_daily_analytics() - deprecated, using individual event logging

            return digest_id
        else:
            logger.error("❌ Failed to save digest with metrics")
            return None

    except Exception as e:
        logger.error(f"❌ Error saving digest with metrics: {e}")
        return None


def update_digest_feedback(digest_id: str, score: float) -> bool:
    """
    Update feedback score for digest.

    Args:
        digest_id: Digest ID
        score: Feedback score (0.0-1.0)

    Returns:
        True if successful, False otherwise
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        # Get current digest data
        result = safe_execute(supabase.table("digests").select("feedback_score", "feedback_count").eq("id", digest_id))

        if not result.data:
            logger.warning(f"Digest {digest_id} not found")
            return False

        current_data = result.data[0]
        current_score = current_data.get("feedback_score", 0.0) or 0.0
        current_count = current_data.get("feedback_count", 0) or 0

        # Calculate new average
        if current_count == 0:
            new_score = score
        else:
            new_score = (current_score * current_count + score) / (current_count + 1)

        new_count = current_count + 1

        # Update digest
        update_result = safe_execute(
            supabase.table("digests")
            .update(
                {
                    "feedback_score": round(new_score, 3),
                    "feedback_count": new_count,
                }
            )
            .eq("id", digest_id)
        )

        if update_result.data:
            logger.info(f"✅ Feedback updated for digest {digest_id}: {score} (avg: {new_score:.3f})")
            return True
        else:
            logger.error(f"❌ Failed to update feedback for digest {digest_id}")
            return False

    except Exception as e:
        logger.error(f"❌ Error updating digest feedback: {e}")
        return False


def get_daily_digest_analytics(date: Optional[str] = None) -> dict:
    """
    Get aggregated analytics for date (default: today).

    Args:
        date: Date in YYYY-MM-DD format (default: today)

    Returns:
        Dictionary with analytics data
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return {}

    try:
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")

        # Try to get from digest_analytics table first (filter by created_at date)
        start_date = f"{date}T00:00:00Z"
        end_date = f"{date}T23:59:59Z"

        result = safe_execute(
            supabase.table("digest_analytics").select("*").gte("created_at", start_date).lte("created_at", end_date)
        )

        if result.data:
            # Агрегируем данные за день
            records = result.data
            total_count = len(records)
            avg_generation_time = (
                sum(r.get("generation_time_ms", 0) for r in records) / total_count / 1000 if total_count > 0 else 0
            )
            success_count = sum(1 for r in records if r.get("success", False))

            logger.debug(f"✅ Retrieved {total_count} analytics records from digest_analytics for {date}")
            return {
                "generated_count": total_count,
                "avg_confidence": 0.0,  # Не хранится в текущей схеме
                "avg_generation_time_sec": avg_generation_time,
                "skipped_low_quality": total_count - success_count,
                "feedback_count": 0,  # Не хранится в текущей схеме
                "avg_feedback_score": 0.0,  # Не хранится в текущей схеме
            }

        # Fallback: calculate from digests table
        logger.debug(f"Calculating analytics from digests table for {date}")

        # Get digests for the date
        start_date = f"{date}T00:00:00Z"
        end_date = f"{date}T23:59:59Z"

        result = safe_execute(
            supabase.table("digests").select("*").gte("created_at", start_date).lte("created_at", end_date).execute()
        )

        if not result.data:
            return {
                "generated_count": 0,
                "avg_confidence": 0.0,
                "avg_generation_time_sec": 0.0,
                "skipped_low_quality": 0,
                "feedback_count": 0,
                "avg_feedback_score": 0.0,
            }

        digests = result.data

        # Calculate metrics
        generated_count = len(digests)
        skipped_low_quality = len([d for d in digests if d.get("skipped_reason")])

        # Confidence metrics
        confidences = [d.get("confidence") for d in digests if d.get("confidence") is not None]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Generation time metrics
        times = [d.get("generation_time_sec") for d in digests if d.get("generation_time_sec") is not None]
        avg_generation_time_sec = sum(times) / len(times) if times else 0.0

        # Feedback metrics
        feedback_scores = [d.get("feedback_score") for d in digests if d.get("feedback_score") is not None]
        avg_feedback_score = sum(feedback_scores) / len(feedback_scores) if feedback_scores else 0.0
        feedback_count = sum(d.get("feedback_count", 0) for d in digests)

        analytics = {
            "generated_count": generated_count,
            "avg_confidence": round(avg_confidence, 3),
            "avg_generation_time_sec": round(avg_generation_time_sec, 2),
            "skipped_low_quality": skipped_low_quality,
            "feedback_count": feedback_count,
            "avg_feedback_score": round(avg_feedback_score, 3),
        }

        logger.debug(f"✅ Calculated analytics for {date}: {analytics}")
        return analytics

    except Exception as e:
        logger.error(f"❌ Error getting digest analytics: {e}")
        return {}


def update_daily_analytics():
    """
    Update digest_analytics with today's aggregated data.
    Note: This function is deprecated as we now log individual digest generation events.
    """
    logger.warning("update_daily_analytics is deprecated - using individual event logging instead")
    return


def get_digest_analytics_history(days: int = 7) -> List[dict]:
    """
    Get digest analytics history for last N days.

    Args:
        days: Number of days to retrieve

    Returns:
        List of analytics data for each day
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return []

    try:
        # Get analytics for last N days
        result = safe_execute(
            supabase.table("digest_analytics").select("*").order("date", desc=True).limit(days).execute()
        )

        if result.data:
            logger.debug(f"✅ Retrieved analytics history for {days} days")
            return result.data
        else:
            logger.debug(f"No analytics history found for {days} days")
            return []

    except Exception as e:
        logger.error(f"❌ Error getting analytics history: {e}")
        return []


# =============================================================================
# USER CATEGORY PREFERENCES FUNCTIONS (JSONB-based)
# =============================================================================


def get_user_category_preferences(user_id: str) -> Dict:
    """
    Получить предпочтения категорий пользователя из JSONB поля.

    Args:
        user_id: User ID (UUID string)

    Returns:
        Dict с предпочтениями категорий:
        {
            "sports": ["football", "basketball"],  # конкретные подкатегории
            "crypto": null,                         # вся категория
            "markets": [],                          # отключена
        }
        Пустой dict {} если предпочтений нет
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return {}

    try:
        result = safe_execute(supabase.table("user_preferences").select("category_preferences").eq("user_id", user_id))

        if result.data and len(result.data) > 0:
            preferences = result.data[0].get("category_preferences", {})
            logger.debug(f"Получены предпочтения для пользователя {user_id}: {preferences}")
            return preferences
        else:
            logger.debug(f"Предпочтения не найдены для пользователя {user_id}, возвращаем пустой dict")
            return {}

    except Exception as e:
        logger.error(f"Ошибка при получении предпочтений пользователя {user_id}: {e}")
        return {}


def upsert_user_category_preferences(user_id: str, preferences: Dict) -> bool:
    """
    Сохранить/обновить предпочтения категорий пользователя.

    Args:
        user_id: User ID (UUID string)
        preferences: Dict с предпочтениями категорий
            {
                "sports": ["football"],
                "crypto": null,
                "markets": []
            }

    Returns:
        True если успешно сохранено, False в противном случае
    """
    if not supabase:
        logger.error("Supabase не инициализирован")
        return False

    try:
        # Upsert preferences (создать или обновить)
        result = safe_execute(
            supabase.table("user_preferences").upsert(
                {
                    "user_id": user_id,
                    "category_preferences": preferences,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                },
                on_conflict="user_id",
            )
        )

        if result.data:
            logger.info(f"✅ Предпочтения сохранены для пользователя {user_id}")
            return True
        else:
            logger.error(f"❌ Не удалось сохранить предпочтения для пользователя {user_id}")
            return False

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении предпочтений пользователя {user_id}: {e}")
        return False


def get_active_categories(user_id: str) -> Dict[str, List[str]]:
    """
    Получить активные категории и подкатегории для фильтрации контента.

    Парсит JSONB структуру и возвращает два списка:
    - full_categories: категории с null (показывать все подкатегории)
    - subcategories: dict категорий с конкретными подкатегориями

    Args:
        user_id: User ID (UUID string)

    Returns:
        Dict с активными категориями:
        {
            'full_categories': ['crypto', 'tech'],  # null в JSONB
            'subcategories': {
                'sports': ['football', 'basketball'],
                'markets': ['earnings']
            }
        }

    Логика:
        - null = включена вся категория → добавляем в full_categories
        - ["sub1", "sub2"] = конкретные подкатегории → добавляем в subcategories
        - [] или отсутствует = отключена → пропускаем
    """
    preferences = get_user_category_preferences(user_id)

    if not preferences:
        # Если предпочтений нет, возвращаем пустые списки
        # (значит показываем весь контент без фильтрации)
        logger.debug(f"Нет предпочтений для пользователя {user_id}, фильтрация не применяется")
        return {"full_categories": [], "subcategories": {}}

    full_categories = []
    subcategories = {}

    for category, value in preferences.items():
        if value is None:
            # null = вся категория включена
            full_categories.append(category)
        elif isinstance(value, list) and len(value) > 0:
            # Список подкатегорий (не пустой)
            subcategories[category] = value
        # Пустой список [] или другие значения = пропускаем (отключена)

    logger.debug(
        f"Активные категории для пользователя {user_id}: " f"full={full_categories}, subcategories={subcategories}"
    )

    return {"full_categories": full_categories, "subcategories": subcategories}
