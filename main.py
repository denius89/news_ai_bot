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
from config.settings import VERSION, DEBUG, WEBAPP_PORT, WEBAPP_HOST, REACTOR_ENABLED
from utils.logging_setup import setup_logging

# PULSE-WS: Import routes
from routes.ws_routes import router as ws_router
from routes.news_routes import news_bp
from routes.webapp_routes import webapp_bp  
from routes.api_routes import api_bp
from routes.metrics_routes import metrics_bp

# PULSE-WS: Setup logging
setup_logging()
logger = logging.getLogger("news_ai_bot")

# PULSE-WS: Create FastAPI app
app = FastAPI(
    title="PulseAI",
    description="AI-Powered News & Events with Reactor Core",
    version=VERSION,
    debug=DEBUG
)

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
app.include_router(ws_router)

# PULSE-WS: Include other routers (convert Flask blueprints to FastAPI routers)
# Note: This will need to be updated to convert Flask routes to FastAPI
# For now, we'll create basic endpoints to maintain functionality

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """PULSE-WS: Root endpoint."""
    return templates.TemplateResponse("index.html", {"request": request, "title": "PulseAI - AI-Powered News & Events"})

@app.get("/digest", response_class=HTMLResponse)
async def digest(request: Request):
    """PULSE-WS: Digest endpoint."""
    return templates.TemplateResponse("digest.html", {"request": request, "title": "Daily Digest"})

@app.get("/events", response_class=HTMLResponse)
async def events(request: Request):
    """PULSE-WS: Events endpoint."""
    return templates.TemplateResponse("events.html", {"request": request, "title": "Events"})

@app.get("/live", response_class=HTMLResponse)
async def live(request: Request):
    """PULSE-WS: Live dashboard endpoint."""
    return templates.TemplateResponse("pages/live_dashboard.html", {"request": request, "title": "Live Dashboard"})

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
                    "timestamp": event.timestamp.isoformat() if hasattr(event.timestamp, 'isoformat') else str(event.timestamp),
                    "id": event.id
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