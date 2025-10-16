"""
GitHub Releases Provider for major project releases.

Fetches release events from GitHub API.
"""

import logging
import os
from datetime import datetime
from typing import Dict, List

import aiohttp

from events.providers.base_provider import BaseEventProvider

logger = logging.getLogger("github_releases_provider")


class GitHubReleasesProvider(BaseEventProvider):
    """
    Provider for GitHub project releases.

    Features:
    - Fetches releases from major projects
    - Requires GitHub token
    - Tracks major software releases
    """

    def __init__(self):
        """Initialize GitHub Releases provider."""
        super().__init__("github_releases", "tech")
        self.base_url = "https://api.github.com"
        self.api_key = os.getenv("GITHUB_TOKEN")

        # Major projects to track (categorized)
        self.tracked_repos = {
            # AI/ML projects
            "ai": [
                "tensorflow/tensorflow",
                "pytorch/pytorch",
                "openai/openai-python",
                "huggingface/transformers",
                "microsoft/DeepSpeed",
                "facebookresearch/llama",
            ],
            # General software
            "software": [
                "kubernetes/kubernetes",
                "nodejs/node",
                "python/cpython",
                "rust-lang/rust",
                "golang/go",
                "microsoft/vscode",
                "docker/docker",
                "facebook/react",
            ],
            # Hardware/Systems
            "hardware": [
                "torvalds/linux",
                "raspberrypi/linux",
                "u-boot/u-boot",
                "NVIDIA/cuda-samples",
            ],
            # Cybersecurity
            "cybersecurity": [
                "metasploit-framework/metasploit-framework",
                "sqlmapproject/sqlmap",
                "OWASP/CheatSheetSeries",
                "openssl/openssl",
                "wireshark/wireshark",
            ],
            # Startups/Tools
            "startups": [
                "vercel/next.js",
                "supabase/supabase",
                "strapi/strapi",
            ],
        }

        # Flatten for backward compatibility
        self.all_repos = []
        for category_repos in self.tracked_repos.values():
            self.all_repos.extend(category_repos)

        if not self.api_key:
            logger.warning("GITHUB_TOKEN not set, provider will be disabled")

    async def fetch_events(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch events from GitHub.

        Args:
            start_date: Start date for fetching
            end_date: End date for fetching

        Returns:
            List of event dictionaries
        """
        if not self.api_key:
            logger.warning("GitHub Releases provider disabled: no API key")
            return []

        try:
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers={
                        "Authorization": f"token {self.api_key}",
                        "Accept": "application/vnd.github.v3+json",
                    }
                )

            events = []

            # Fetch releases for each tracked repo
            for repo in self.all_repos:
                repo_events = await self._fetch_repo_releases(repo, start_date, end_date)
                events.extend(repo_events)

            logger.info(f"Fetched {len(events)} events from GitHub Releases")
            return events

        except Exception as e:
            logger.error(f"Error fetching GitHub Releases events: {e}")
            return []

    async def _fetch_repo_releases(self, repo: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Fetch releases for a specific repository."""
        try:
            url = f"{self.base_url}/repos/{repo}/releases"
            params = {"per_page": 10}

            # Apply rate limit (Authenticated: 5000 req/hour = ~83 req/min)
            await self.rate_limiter.acquire()

            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    logger.error(f"GitHub API error for {repo}: {response.status}")
                    return []

                releases = await response.json()

                events = []
                for release in releases:
                    event = self._parse_release(release, repo, start_date, end_date)
                    if event:
                        normalized = self.normalize_event(event)
                        if normalized:
                            events.append(normalized)

                return [e for e in events if e is not None]

        except Exception as e:
            logger.error(f"Error fetching releases for {repo}: {e}")
            return []

    def _parse_release(self, release: Dict, repo: str, start_date: datetime, end_date: datetime) -> Dict:
        """Parse release to standard format."""
        try:
            tag_name = release.get("tag_name", "")
            name = release.get("name", tag_name)

            if not name:
                return None

            # Parse published date
            published_at_str = release.get("published_at")
            if not published_at_str:
                return None

            published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))

            # Filter by date range
            if not (start_date <= published_at <= end_date):
                return None

            # Determine importance based on release type
            is_prerelease = release.get("prerelease", False)
            importance = 0.6 if is_prerelease else 0.8

            # Extract project name from repo
            project_name = repo.split("/")[1]

            # Determine subcategory based on repo
            subcategory = self._determine_subcategory(repo, tag_name)

            return {
                "title": f"{project_name} {tag_name} Released",
                "starts_at": published_at,
                "ends_at": None,
                "subcategory": subcategory,
                "importance": importance,
                "description": release.get("body", "")[:500],  # Limit description length
                "link": release.get("html_url", ""),
                "location": "GitHub",
                "organizer": repo.split("/")[0] or "Open Source Community",
                "group_name": project_name,
                "metadata": {
                    "repo": repo,
                    "project": project_name,
                    "version": tag_name,
                    "tag_name": tag_name,
                    "is_prerelease": is_prerelease,
                    "author": release.get("author", {}).get("login"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing release: {e}")
            return None

    def _determine_subcategory(self, repo: str, tag_name: str) -> str:
        """Determine subcategory based on repository."""
        # Check category from tracked_repos
        for category, repos in self.tracked_repos.items():
            if repo in repos:
                return category

        # Fallback: parse from repo name
        repo_lower = repo.lower()
        if any(word in repo_lower for word in ["ai", "ml", "deep", "neural", "llm", "gpt", "transformers"]):
            return "ai"
        elif any(word in repo_lower for word in ["linux", "kernel", "driver", "hardware", "cuda", "gpu"]):
            return "hardware"
        elif any(word in repo_lower for word in ["security", "crypto", "ssl", "auth", "vuln", "hack"]):
            return "cybersecurity"
        elif any(word in repo_lower for word in ["startup", "saas", "platform"]):
            return "startups"
        else:
            return "software"
