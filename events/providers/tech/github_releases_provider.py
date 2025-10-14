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

        # Major projects to track
        self.tracked_repos = [
            "kubernetes/kubernetes",
            "nodejs/node",
            "python/cpython",
            "rust-lang/rust",
            "golang/go",
            "microsoft/vscode",
            "docker/docker",
            "tensorflow/tensorflow",
            "pytorch/pytorch",
            "facebook/react",
        ]

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
            for repo in self.tracked_repos:
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

            return {
                "title": f"{project_name} {tag_name} Released",
                "starts_at": published_at,
                "ends_at": None,
                "subcategory": "software_release",
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
