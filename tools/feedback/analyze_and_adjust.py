#!/usr/bin/env python3
"""
Background Job: Feedback Analysis and Auto-Adjustment
Purpose: Analyze user feedback correlations and adjust AI parameters
Schedule: Daily at 2 AM via cron
"""

import sys
import os
import logging
import json
from datetime import datetime
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.db_models import supabase
from ai_modules.feedback_loop import FeedbackLoopManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/feedback_analysis.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def main():
    """Main job function."""
    job_name = "feedback_analysis"
    start_time = datetime.utcnow()

    logger.info(json.dumps({"event": "job_start", "job": job_name, "start_time": start_time.isoformat()}))

    try:
        if not supabase:
            logger.error("Supabase client not initialized")
            return 1

        # Initialize feedback loop manager
        manager = FeedbackLoopManager(supabase)

        # Run analysis for last 7 days
        result = manager.run_feedback_analysis(days=7)

        if result.get("status") != "success":
            logger.warning(f"Feedback analysis had issues: {result}")
            return 1

        # Log results
        correlations = result.get("correlations", {})
        adjustments = result.get("adjustments", {})

        logger.info(
            json.dumps(
                {
                    "event": "analysis_results",
                    "sample_size": correlations.get("sample_size", 0),
                    "importance_correlation": correlations.get("importance_correlation", 0),
                    "credibility_correlation": correlations.get("credibility_correlation", 0),
                    "recommendations_count": len(correlations.get("recommendations", [])),
                    "adjustments": adjustments,
                }
            )
        )

        # TODO: Apply adjustments to config/data/ai_optimization.yaml
        # This would be implemented in a separate config update function

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        logger.info(
            json.dumps(
                {
                    "event": "job_complete",
                    "job": job_name,
                    "duration_sec": duration,
                    "success": True,
                    "recommendations": correlations.get("recommendations", []),
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

