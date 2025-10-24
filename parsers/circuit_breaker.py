"""
Circuit Breaker для временной блокировки проблемных доменов.

Предотвращает cascading failures и уважает источники, которые испытывают проблемы.
"""

import time
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """
    Временно блокирует проблемные домены для предотвращения
    cascading failures и уважения к источникам.

    После fail_threshold неудач домен блокируется на cool_down секунд.

    Example:
        cb = CircuitBreaker(fail_threshold=5, cool_down=300)

        if cb.allow("espn.com"):
            result = fetch("https://espn.com/feed")
            cb.report("espn.com", success=True)
        else:
            # Домен заблокирован, пропускаем
            pass
    """

    def __init__(self, fail_threshold: int = 5, cool_down: int = 300):
        """
        Args:
            fail_threshold: Количество неудач для открытия circuit breaker
            cool_down: Время блокировки в секундах
        """
        self.failures: Dict[str, int] = {}
        self.blocked_until: Dict[str, float] = {}
        self.fail_threshold = fail_threshold
        self.cool_down = cool_down

        logger.info(f"Circuit breaker initialized: " f"fail_threshold={fail_threshold}, cool_down={cool_down}s")

    def allow(self, domain: str) -> bool:
        """
        Проверяет можно ли делать запрос к домену

        Args:
            domain: Доменное имя (например, "espn.com")

        Returns:
            True если запросы разрешены, False если домен заблокирован
        """
        now = time.time()
        blocked_until = self.blocked_until.get(domain, 0)

        if now >= blocked_until:
            return True

        remaining = int(blocked_until - now)
        logger.debug(f"Circuit breaker: {domain} blocked for {remaining}s")
        return False

    def report(self, domain: str, success: bool):
        """
        Отчет о результате запроса

        Args:
            domain: Доменное имя
            success: True если запрос успешен, False если провален
        """
        if success:
            # Успех - сбросить счетчик
            self.failures[domain] = 0

            # Разблокировать если был заблокирован
            if domain in self.blocked_until:
                del self.blocked_until[domain]
                logger.info(f"✓ Circuit breaker: {domain} recovered")
        else:
            # Неудача - увеличить счетчик
            self.failures[domain] = self.failures.get(domain, 0) + 1

            # Проверить порог
            if self.failures[domain] >= self.fail_threshold:
                self.blocked_until[domain] = time.time() + self.cool_down
                logger.warning(
                    f"⚠️ Circuit breaker OPEN for {domain} "
                    f"({self.failures[domain]} failures, {self.cool_down}s cooldown)"
                )

    def get_stats(self) -> dict:
        """
        Статистика для мониторинга

        Returns:
            Dict с метриками circuit breaker
        """
        now = time.time()

        # Фильтровать только активно заблокированные домены
        active_blocks = {
            domain: blocked_until for domain, blocked_until in self.blocked_until.items() if blocked_until > now
        }

        return {
            "blocked_domains": len(active_blocks),
            "domains_with_failures": len([f for f in self.failures.values() if f > 0]),
            "blocked_list": list(active_blocks.keys()),
            "total_domains_tracked": len(self.failures),
        }

    def reset(self, domain: str = None):
        """
        Сбросить состояние circuit breaker

        Args:
            domain: Если указан - сбросить только этот домен, иначе все
        """
        if domain:
            self.failures.pop(domain, None)
            self.blocked_until.pop(domain, None)
            logger.info(f"Circuit breaker reset for {domain}")
        else:
            self.failures.clear()
            self.blocked_until.clear()
            logger.info("Circuit breaker reset for all domains")
