"""
Legacy RSS Parser - теперь использует UnifiedParser.

Этот модуль сохранен для обратной совместимости.
Все новые разработки должны использовать parsers.unified_parser.
"""

from parsers.unified_parser import (
    UnifiedParser,
    parse_source,
    parse_all_sources,
    get_sync_parser,
    get_async_parser,
)

# Экспортируем функции для обратной совместимости
__all__ = [
    "UnifiedParser",
    "parse_source",
    "parse_all_sources",
    "get_sync_parser",
    "get_async_parser",
]
