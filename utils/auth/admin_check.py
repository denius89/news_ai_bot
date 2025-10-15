"""
Admin access control для PulseAI Admin Panel.

Предоставляет декораторы для защиты admin endpoints и проверки прав доступа.
Использует существующую Telegram auth из webapp.py middleware.
"""

from functools import wraps
from flask import g, jsonify, session
from database.service import get_sync_service
import logging

logger = logging.getLogger(__name__)


def is_admin(telegram_id: int) -> bool:
    """
    Проверяет, является ли пользователь админом (с кешированием в session).

    Args:
        telegram_id: Telegram ID пользователя

    Returns:
        True если пользователь активный админ, иначе False
    """
    # Быстрая проверка через session cache
    if session.get("is_admin") and session.get("admin_telegram_id") == telegram_id:
        logger.debug(f"Admin check (cached): {telegram_id}")
        return True

    try:
        db = get_sync_service()
        result = db.safe_execute(
            db.sync_client.table("admins").select("is_active").eq("telegram_id", telegram_id).single()
        )

        is_active = result.data and result.data.get("is_active", False)

        if is_active:
            # Кешируем в session
            session["is_admin"] = True
            session["admin_telegram_id"] = telegram_id
            logger.info(f"✅ Admin access granted: {telegram_id}")
        else:
            logger.warning(f"❌ Admin access denied: {telegram_id} (not in admins table or inactive)")

        return is_active

    except Exception as e:
        logger.error(f"Admin check failed for {telegram_id}: {e}")
        return False


def require_admin(f):
    """
    Decorator для защиты admin API endpoints.

    Использует СУЩЕСТВУЮЩУЮ Telegram auth из middleware webapp.py.
    Проверяет наличие g.current_user и is_admin статус.

    В DEBUG режиме (для разработки) пропускает проверку для localhost.

    Usage:
        @admin_bp.route('/stats')
        @require_admin
        def get_stats():
            return jsonify({'data': '...'})
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        from config.core.settings import DEBUG
        from flask import request

        # DEV режим: пропускаем аутентификацию для localhost и Cloudflare tunnel
        is_localhost = request.remote_addr in ["127.0.0.1", "localhost", "::1"]
        is_cloudflare_tunnel = request.headers.get("Host", "").endswith(".trycloudflare.com")

        if DEBUG and (is_localhost or is_cloudflare_tunnel):
            logger.info(
                f"🔓 DEV mode: bypassing admin auth for {request.remote_addr} (localhost: {is_localhost}, tunnel: {is_cloudflare_tunnel})"
            )
            # Создаём fake admin session для DEV
            g.admin_id = 999999999  # fake dev admin ID
            session["is_admin"] = True
            session["admin_telegram_id"] = 999999999
            return f(*args, **kwargs)

        # Используем СУЩЕСТВУЮЩУЮ Telegram auth из middleware webapp.py
        if not hasattr(g, "current_user"):
            logger.warning("Admin endpoint accessed without authentication")
            return jsonify({"error": "Unauthorized", "message": "Please authenticate via Telegram"}), 401

        telegram_id = g.current_user.get("telegram_id")
        if not telegram_id:
            logger.warning("Admin endpoint accessed without telegram_id")
            return jsonify({"error": "Unauthorized", "message": "Invalid user data"}), 401

        if not is_admin(telegram_id):
            logger.warning(f"Non-admin user attempted to access admin endpoint: {telegram_id}")
            return jsonify({"error": "Forbidden", "message": "Admin access required"}), 403

        # Обновляем last_login в фоне (non-blocking)
        try:
            db = get_sync_service()
            db.safe_execute(
                db.sync_client.table("admins").update({"last_login": "NOW()"}).eq("telegram_id", telegram_id)
            )
        except Exception as e:
            logger.warning(f"Failed to update last_login for {telegram_id}: {e}")

        # Передаем в endpoint через g
        g.admin_id = telegram_id

        return f(*args, **kwargs)

    return wrapper


def get_admin_info(telegram_id: int) -> dict:
    """
    Получает информацию об админе из БД.

    Args:
        telegram_id: Telegram ID админа

    Returns:
        Dict с информацией об админе или None
    """
    from config.core.settings import DEBUG

    # DEV режим: возвращаем fake admin info
    if DEBUG and telegram_id == 999999999:
        return {
            "telegram_id": 999999999,
            "username": "dev_admin",
            "is_active": True,
            "created_at": "2025-10-15T00:00:00",
            "last_login": "2025-10-15T00:00:00",
        }

    try:
        db = get_sync_service()
        result = db.safe_execute(db.sync_client.table("admins").select("*").eq("telegram_id", telegram_id).single())
        return result.data
    except Exception as e:
        logger.error(f"Failed to get admin info for {telegram_id}: {e}")
        return None
