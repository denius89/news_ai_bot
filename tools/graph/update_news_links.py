#!/usr/bin/env python3
"""
Background Job: News Graph Update
Purpose: Update news links and build story context graph
Schedule: Daily at 4 AM via cron
"""

import sys
import os
import logging
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_models import supabase
from ai_modules.news_graph import NewsGraphBuilder

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/news_graph_update.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main():
    """Main job function."""
    job_name = "news_graph_update"
    start_time = datetime.utcnow()

    logger.info(json.dumps({"event": "job_start", "job": job_name, "start_time": start_time.isoformat()}))

    try:
        if not supabase:
            logger.error("Supabase client not initialized")
            return 1

        # Initialize news graph builder
        graph_builder = NewsGraphBuilder(supabase)

        # Get recent news (last 7 days)
        end_date = datetime.now(timezone.utc).isoformat()
        start_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

        recent_news = (
            supabase.table("news")
            .select("*")
            .gte("created_at", start_date)
            .lte("created_at", end_date)
            .order("created_at", desc=True)
            .limit(100)
            .execute()
        )

        if not recent_news.data:
            logger.info("No recent news found for graph update")
            return 0

        logger.info(f"Processing {len(recent_news.data)} recent news items")

        # Process each news item and find related news
        links_created = 0

        for news_item in recent_news.data[:20]:  # Limit to avoid overloading
            try:
                # Find related news
                related_news = graph_builder.find_related_news(news_item, lookback_days=30, max_results=5)

                # Save links for high similarity news
                for related in related_news:
                    if related.get("similarity_score", 0) > 0.4:  # Threshold
                        success = graph_builder.save_news_links(
                            news_id_1=news_item["id"],
                            news_id_2=related["id"],
                            link_type="related",
                            similarity_score=related["similarity_score"],
                            keywords_overlap=related.get("keywords_overlap", {}),
                            entities_overlap=related.get("entities_overlap", {}),
                        )

                        if success:
                            links_created += 1

            except Exception as e:
                logger.warning(f"Error processing news item {news_item.get('id', 'unknown')}: {e}")
                continue

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        logger.info(
            json.dumps(
                {
                    "event": "job_complete",
                    "job": job_name,
                    "duration_sec": duration,
                    "news_processed": len(recent_news.data[:20]),
                    "links_created": links_created,
                    "success": True,
                }
            )
        )

        return 0

    except Exception as e:
        logger.error(
            json.dumps(
                {
                    "event": "job_failed",
                    "job": job_name,
                    "error": str(e),
                    "duration_sec": (datetime.utcnow() - start_time).total_seconds(),
                }
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
