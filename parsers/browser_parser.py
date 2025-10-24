"""
Module: parsers.browser_parser
Purpose: Browser-based parsing with Playwright for complex sources
Location: parsers/browser_parser.py

Description:
    Система парсинга сложных источников с использованием Playwright:
    - JavaScript rendering
    - Anti-bot bypassing
    - Dynamic content extraction
    - Cloudflare detection and handling
    - Optimized resource loading

Author: PulseAI Team
Last Updated: January 2025
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
except ImportError:
    async_playwright = None
    Browser = None
    BrowserContext = None
    Page = None

logger = logging.getLogger(__name__)


class BrowserParser:
    """
    Парсер с использованием браузера для сложных источников
    """

    def __init__(self, headless: bool = True, timeout: int = 30000):
        """
        Инициализация Browser Parser

        Args:
            headless: Запуск в headless режиме
            timeout: Таймаут для операций браузера в мс
        """
        if not async_playwright:
            raise ImportError(
                "Playwright не установлен. Установите: pip install playwright && playwright install chromium"
            )

        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        # Cloudflare detection patterns
        self.cloudflare_patterns = [
            "Checking your browser",
            "Just a moment",
            "Please wait while we check your browser",
            "DDoS protection by Cloudflare",
            "cf-browser-verification",
        ]

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        await self._init_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        await self.close()

    async def _init_browser(self):
        """Инициализация браузера"""
        if self.browser:
            return

        try:
            self.playwright = await async_playwright().start()

            # Launch browser with optimized settings
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-extensions",
                    "--disable-plugins",
                    "--disable-images",  # Skip loading images for speed
                    "--disable-javascript",  # We'll enable selectively
                    "--block-loading-lazily",
                    "--aggressive-cache-discard",
                ],
            )

            # Create context with realistic settings
            self.context = await self.browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
                viewport={"width": 1920, "height": 1080},
                locale="en-US",
                timezone_id="America/New_York",
            )

            logger.info("Browser initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            await self.close()
            raise

    async def close(self):
        """Закрытие браузера и освобождение ресурсов"""
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if hasattr(self, "playwright") and self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def detect_cloudflare(self, page: Page) -> bool:
        """
        Детектирование Cloudflare защиты

        Args:
            page: Страница для проверки

        Returns:
            True если обнаружен Cloudflare
        """
        try:
            # Check page content for Cloudflare patterns
            content = await page.content()
            for pattern in self.cloudflare_patterns:
                if pattern in content:
                    logger.debug(f"Cloudflare detected: {pattern}")
                    return True

            # Check for Cloudflare specific elements
            cloudflare_elements = await page.locator("[data-ray]").count()
            if cloudflare_elements > 0:
                logger.debug("Cloudflare elements detected")
                return True

            return False

        except Exception as e:
            logger.debug(f"Cloudflare detection failed: {e}")
            return False

    async def wait_for_content_load(self, page: Page, max_wait: int = 10000) -> bool:
        """
        Ожидание загрузки контента с проверкой Cloudflare

        Args:
            page: Страница для ожидания
            max_wait: Максимальное время ожидания в мс

        Returns:
            True если контент загружен успешно
        """
        try:
            start_time = time.time()

            while (time.time() - start_time) * 1000 < max_wait:
                # Check if Cloudflare is blocking
                if await self.detect_cloudflare(page):
                    logger.debug("Cloudflare detected, waiting...")
                    await page.wait_for_timeout(2000)
                    continue

                # Check if main content is loaded
                content_ready = await page.evaluate(
                    """
                    () => {
                        return document.readyState === 'complete' &&
                               document.querySelector('article, main, .content, .post, .entry') !== null;
                    }
                """
                )

                if content_ready:
                    return True

                await page.wait_for_timeout(500)

            # Final check for Cloudflare
            if await self.detect_cloudflare(page):
                logger.warning("Cloudflare blocking detected after timeout")
                return False

            return True

        except Exception as e:
            logger.debug(f"Content load wait failed: {e}")
            return False

    async def extract_content_with_selectors(self, page: Page, url: str) -> Dict[str, Any]:
        """
        Извлечение контента с использованием CSS селекторов

        Args:
            page: Страница для извлечения
            url: URL страницы

        Returns:
            Словарь с извлеченным контентом
        """
        try:
            # Common content selectors ordered by preference
            content_selectors = [
                "article",
                ".post-content",
                ".entry-content",
                ".content",
                ".article-content",
                "main",
                ".main-content",
                "[role='main']",
                ".post",
                ".entry",
            ]

            # Extract title
            title = ""
            title_selectors = ["h1", ".entry-title", ".post-title", "title"]
            for selector in title_selectors:
                try:
                    title_element = await page.locator(selector).first
                    if await title_element.count() > 0:
                        title = (await title_element.text_content() or "").strip()
                        if title and len(title) > 10:
                            break
                except Exception:
                    continue

            # Extract main content
            content = ""
            for selector in content_selectors:
                try:
                    content_element = await page.locator(selector).first
                    if await content_element.count() > 0:
                        content = await content_element.inner_text()
                        if content and len(content) > 100:
                            break
                except Exception:
                    continue

            # Fallback: extract from body
            if not content:
                try:
                    content = await page.locator("body").inner_text()
                except Exception:
                    content = ""

            # Clean content
            content = content.replace("\n", " ").replace("\t", " ")
            content = " ".join(content.split())

            return {"title": title, "content": content, "url": url, "success": bool(title and content)}

        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return {"title": "", "content": "", "url": url, "success": False, "error": str(e)}

    async def parse_page(self, url: str, enable_js: bool = True) -> Dict[str, Any]:
        """
        Парсинг страницы с использованием браузера

        Args:
            url: URL для парсинга
            enable_js: Включить JavaScript (для динамического контента)

        Returns:
            Словарь с результатами парсинга
        """
        if not self.context:
            await self._init_browser()

        page = None
        try:
            # Create new page
            page = await self.context.new_page()

            # Set timeout
            page.set_default_timeout(self.timeout)

            # Navigate to URL
            logger.debug(f"Navigating to {url}")
            response = await page.goto(url, wait_until="domcontentloaded")

            if not response or response.status >= 400:
                return {
                    "title": "",
                    "content": "",
                    "url": url,
                    "success": False,
                    "error": f"HTTP {response.status if response else 'no response'}",
                }

            # Enable JavaScript if needed
            if enable_js:
                await page.add_init_script(
                    """
                    // Disable some resource types for speed
                    if (window.chrome) {
                        const originalFetch = window.fetch;
                        window.fetch = function(...args) {
                            return originalFetch.apply(this, args);
                        };
                    }
                """
                )

            # Wait for content to load
            content_loaded = await self.wait_for_content_load(page)
            if not content_loaded:
                return {
                    "title": "",
                    "content": "",
                    "url": url,
                    "success": False,
                    "error": "Content load timeout or Cloudflare blocking",
                }

            # Extract content
            result = await self.extract_content_with_selectors(page, url)

            return result

        except Exception as e:
            logger.error(f"Page parsing failed for {url}: {e}")
            return {"title": "", "content": "", "url": url, "success": False, "error": str(e)}
        finally:
            if page:
                await page.close()

    async def parse_multiple_pages(
        self, urls: List[str], enable_js: bool = True, max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Парсинг нескольких страниц с ограничением concurrency

        Args:
            urls: Список URL для парсинга
            enable_js: Включить JavaScript
            max_concurrent: Максимальное количество одновременных запросов

        Returns:
            Список результатов парсинга
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def parse_with_semaphore(url: str) -> Dict[str, Any]:
            async with semaphore:
                return await self.parse_page(url, enable_js)

        tasks = [parse_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    {"title": "", "content": "", "url": urls[i], "success": False, "error": str(result)}
                )
            else:
                processed_results.append(result)

        return processed_results
