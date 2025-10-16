"""
Digest Service - shim module for backward compatibility.

This module re-exports the new DigestAIService and related components
to maintain backward compatibility with existing code.
"""

# Re-export main components from ai_service (within digests module)
from digests.ai_service import (
    DigestAIService,
    DigestConfig,
    generate_ai_digest,
    generate_fallback_digest,
)

# Re-export NewsItem from models
from models.news import NewsItem

# Backward compatibility aliases
DigestService = DigestAIService  # Alias for old name

__all__ = [
    "DigestAIService",
    "DigestService",  # Backward compatibility
    "DigestConfig",
    "NewsItem",
    "generate_ai_digest",
    "generate_fallback_digest",
]
