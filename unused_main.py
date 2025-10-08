"""
PULSE-WS: FastAPI application with WebSocket support for PulseAI Reactor.
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# PULSE-WS: Import configuration
# from config.settings import VERSION, DEBUG, WEBAPP_PORT, WEBAPP_HOST, REACTOR_ENABLED
# from utils.logging_setup import setup_logging

# PULSE-WS: Import routes
# from routes.ws_routes import router as ws_router
# from routes.news_routes import news_bp
# from routes.webapp_routes import webapp_bp
# from routes.api_routes import api_bp
# from routes.metrics_routes import metrics_bp

# PULSE-WS: Setup logging
# setup_logging()
logger = logging.getLogger("news_ai_bot")

# PULSE-WS: Hardcoded values to avoid circular imports
VERSION = "0.1.0"
DEBUG = True
WEBAPP_PORT = 8001
WEBAPP_HOST = "0.0.0.0"
REACTOR_ENABLED = False

# PULSE-WS: Create FastAPI app
app = FastAPI(title="PulseAI", description="AI-Powered News & Events with Reactor Core", version=VERSION, debug=DEBUG)

# PULSE-WS: Configure CORS for WebSocket
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PULSE-WS: Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# PULSE-WS: Setup templates
templates = Jinja2Templates(directory="templates")


# PULSE-WS: Add url_for function to template context
def url_for(request: Request, name: str, **path_params):
    """FastAPI equivalent of Flask's url_for."""
    if name == "static":
        # For static files, construct the URL manually
        filename = path_params.get("filename", "")
        return f"/static/{filename}"
    else:
        # For other routes, use FastAPI's url_for
        return request.url_for(name, **path_params)


# PULSE-WS: Add url_for to template context
templates.env.globals["url_for"] = url_for

# PULSE-WS: Add config to template context
from config.settings import REACTOR_ENABLED

templates.env.globals["config"] = type("Config", (), {"REACTOR_ENABLED": REACTOR_ENABLED})()


# PULSE-WS: Add template filters
def importance_icon(value: float) -> str:
    """Filter for displaying importance icons."""
    if value is None:
        return "❔"
    if value >= 0.8:
        return "🔥"
    elif value >= 0.5:
        return "⚡"
    return "💤"


def credibility_icon(value: float) -> str:
    """Filter for displaying credibility icons."""
    if value is None:
        return "❔"
    if value >= 0.8:
        return "✅"
    elif value >= 0.5:
        return "⚠️"
    return "❌"


# PULSE-WS: Add filters to Jinja2 environment
templates.env.filters["importance_icon"] = importance_icon
templates.env.filters["credibility_icon"] = credibility_icon

# PULSE-WS: Include WebSocket router
# app.include_router(ws_router)  # Disabled to avoid circular imports

# PULSE-WS: Include other routers (convert Flask blueprints to FastAPI routers)
# Note: This will need to be updated to convert Flask routes to FastAPI
# For now, we'll create basic endpoints to maintain functionality


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """PULSE-WS: Root endpoint."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "PulseAI - AI-Powered News & Events",
            "url_for": lambda name, **kwargs: url_for(request, name, **kwargs),
        },
    )


@app.get("/digest", response_class=HTMLResponse)
async def digest(request: Request):
    """PULSE-WS: Digest endpoint."""
    # Get categories from query parameters
    categories = request.query_params.getlist("category")

    # Import services
    from services.unified_digest_service import get_sync_digest_service
    from routes.news_routes import get_categories

    try:
        digest_service = get_sync_digest_service()
        digest_text = digest_service.build_daily_digest(limit=10, categories=categories)

        # Get news items for template
        news_items = digest_service.db_service.get_latest_news(categories=categories, limit=10)

        # Enrich data for template
        enriched_items = []
        for item in news_items:
            # Convert Pydantic model to dict for template
            if hasattr(item, "model_dump"):
                item_dict = item.model_dump()
            else:
                item_dict = dict(item)

            item_dict["source"] = item_dict.get("source") or "—"
            item_dict["credibility"] = float(item_dict.get("credibility") or 0.0)
            item_dict["importance"] = float(item_dict.get("importance") or 0.0)
            item_dict["published_at_fmt"] = item_dict.get("published_at_fmt") or "—"
            enriched_items.append(item_dict)

        return templates.TemplateResponse(
            "digest.html",
            {
                "request": request,
                "title": "Daily Digest",
                "url_for": lambda name, **kwargs: url_for(request, name, **kwargs),
                "news": enriched_items,
                "all_categories": get_categories(),
                "active_categories": categories,
                "digest_text": digest_text,
                "active_page": "digest",
            },
        )
    except Exception as e:
        logger.error(f"Error in digest endpoint: {e}")
        # Return minimal template with error info
        return templates.TemplateResponse(
            "digest.html",
            {
                "request": request,
                "title": "Daily Digest",
                "url_for": lambda name, **kwargs: url_for(request, name, **kwargs),
                "news": [],
                "all_categories": [],
                "active_categories": categories,
                "digest_text": f"Ошибка загрузки данных: {str(e)}",
                "active_page": "digest",
            },
        )


@app.get("/events", response_class=HTMLResponse)
async def events(request: Request):
    """PULSE-WS: Events endpoint."""
    return templates.TemplateResponse(
        "events.html",
        {"request": request, "title": "Events", "url_for": lambda name, **kwargs: url_for(request, name, **kwargs)},
    )


@app.get("/live", response_class=HTMLResponse)
async def live(request: Request):
    """PULSE-WS: Live dashboard endpoint."""
    return templates.TemplateResponse(
        "pages/live_dashboard.html",
        {
            "request": request,
            "title": "Live Dashboard",
            "url_for": lambda name, **kwargs: url_for(request, name, **kwargs),
        },
    )


@app.get("/webapp", response_class=HTMLResponse)
async def webapp(request: Request):
    """PULSE-WS: WebApp Dashboard endpoint."""
    logger.info("📱 WebApp dashboard accessed")
    return templates.TemplateResponse(
        "webapp.html",
        {
            "request": request,
            "title": "WebApp Dashboard",
            "url_for": lambda name, **kwargs: url_for(request, name, **kwargs),
        },
    )


@app.get("/metrics")
async def metrics():
    """PULSE-WS: Metrics endpoint."""
    from routes.metrics_routes import get_metrics_endpoint

    return get_metrics_endpoint()


@app.get("/latest")
async def latest():
    """PULSE-WS: Latest news endpoint."""
    from routes.news_routes import api_latest_news

    return api_latest_news()


# PULSE-WS: Health check
@app.get("/health")
async def health():
    """PULSE-WS: Health check endpoint."""
    return {"status": "healthy", "version": VERSION}


# PULSE-WS: API endpoints
@app.get("/api/categories")
async def get_categories_api():
    """PULSE-WS: API endpoint для получения категорий."""
    try:
        from services.categories import get_category_structure, get_emoji_icon

        structure = get_category_structure()

        # Преобразуем в формат для WebApp
        categories_data = {}
        for category, subcategories in structure.items():
            categories_data[category] = {
                "name": category.title(),
                "icon": get_emoji_icon(category, ""),
                "emoji": get_emoji_icon(category, ""),  # Добавляем emoji для удобства
                "subcategories": {},
            }

            for subcategory, data in subcategories.items():
                categories_data[category]["subcategories"][subcategory] = {
                    "name": subcategory.title(),
                    "icon": data.get("icon", ""),
                    "emoji": get_emoji_icon(category, subcategory),
                    "sources_count": len(data.get("sources", [])),
                }

        return {
            "status": "success",
            "data": categories_data,
            "total_categories": len(categories_data),
            "total_subcategories": sum(len(cat["subcategories"]) for cat in categories_data.values()),
        }

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/api/user_notifications")
async def get_user_notifications_api(user_id: str = None, limit: int = 50, offset: int = 0):
    """PULSE-WS: API endpoint для получения уведомлений пользователя."""
    if not user_id:
        return {"status": "error", "message": "user_id parameter is required"}

    try:
        # Convert user_id - try UUID format first, then fallback to int
        if len(user_id) == 36 and user_id.count("-") == 4:
            # It's a UUID
            final_user_id = user_id
            logger.info("Using UUID directly: %s", final_user_id)
        else:
            try:
                # Try to convert to int and then get UUID from users table
                telegram_id = int(user_id)
                logger.info("Converting telegram_id to UUID: %d", telegram_id)
                # Get UUID from users table
                from database.db_models import get_user_by_telegram

                user_data = get_user_by_telegram(telegram_id)
                if user_data:
                    final_user_id = user_data.get("id")
                    logger.info("Final user_id for query: %s", final_user_id)
                else:
                    # Fallback to demo UUID
                    final_user_id = "f7d38911-4e62-4012-a9bf-2aaa03483497"
                    logger.warning("Invalid user_id format, using fallback: %s", final_user_id)
            except (ValueError, TypeError):
                # Fallback to demo UUID
                final_user_id = "f7d38911-4e62-4012-a9bf-2aaa03483497"
                logger.warning("Invalid user_id format, using fallback: %s", final_user_id)

        logger.info("Final user_id for query: %s", final_user_id)

        # Get notifications
        from database.db_models import get_user_notifications

        logger.info("Calling get_user_notifications with user_id=%s, limit=%d", final_user_id, limit)

        notifications = get_user_notifications(user_id=final_user_id, limit=limit, offset=offset)
        logger.info("get_user_notifications returned %d notifications", len(notifications))

        return {
            "notifications": notifications,
            "status": "success",
            "count": len(notifications),
            "user_id": final_user_id,
        }

    except Exception as e:
        logger.error("Error getting user notifications: %s", e)
        return {"status": "error", "message": str(e)}


# PULSE-WS: Reactor integration
if REACTOR_ENABLED:
    try:
        from core.reactor import reactor, Events
        from routes.ws_routes import ws_broadcast

        # PULSE-WS: Subscribe to reactor events
        async def handle_reactor_event(event):
            """Handle reactor events and broadcast via WebSocket."""
            try:
                event_data = {
                    "type": event.name,
                    "data": event.data,
                    "source": event.source,
                    "timestamp": (
                        event.timestamp.isoformat() if hasattr(event.timestamp, "isoformat") else str(event.timestamp)
                    ),
                    "id": event.id,
                }
                await ws_broadcast(event_data)
            except Exception as e:
                logger.error(f"PULSE-WS: Error broadcasting reactor event: {e}")

        # PULSE-WS: Subscribe to reactor events
        reactor.on(Events.AI_METRICS_UPDATED, handle_reactor_event)
        reactor.on(Events.NEWS_PROCESSED, handle_reactor_event)
        reactor.on(Events.DIGEST_CREATED, handle_reactor_event)
        reactor.on(Events.EVENT_DETECTED, handle_reactor_event)
        reactor.on(Events.USER_ACTION, handle_reactor_event)
        reactor.on(Events.SYSTEM_HEALTH_CHECK, handle_reactor_event)
        reactor.on(Events.REACTOR_HEARTBEAT, handle_reactor_event)

        logger.info("✅ PULSE-WS: Reactor integration enabled")
    except Exception as e:
        logger.error(f"❌ PULSE-WS: Reactor integration failed: {e}")
else:
    logger.info("⚠️ PULSE-WS: Reactor disabled, WebSocket events will not be available")

if __name__ == "__main__":
    import uvicorn

    logger.info(f"🚀 PULSE-WS: Starting FastAPI app on {WEBAPP_HOST}:{WEBAPP_PORT}")
    uvicorn.run(app, host=WEBAPP_HOST, port=WEBAPP_PORT, log_level="info" if not DEBUG else "debug")
