"""German job-board discovery through public search indexes.

The job boards below do not expose a stable public search API.  This adapter
uses each board's public, indexed job URLs instead of copying their private
application endpoints.  It is intentionally Germany-only and fault-isolated:
a source being unavailable must never stop the main search.
"""

from __future__ import annotations

import hashlib
import logging
import re
from typing import List, Set
from urllib.parse import quote_plus, urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

from .base import BaseJobSource, UnifiedJob

logger = logging.getLogger(__name__)


class GermanJobBoardSource(BaseJobSource):
    """Find public German listings from one job board via its indexed pages."""

    SEARCH_URL = "https://www.bing.com/search?format=rss&q="
    GERMANY_HINTS = (
        "germany", "deutschland", "berlin", "munich", "münchen", "hamburg",
        "frankfurt", "cologne", "köln", "düsseldorf", "stuttgart", "leipzig",
        "dresden", "hannover", "nuremberg", "nürnberg",
    )
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9,de;q=0.8,ar;q=0.7",
    }

    def __init__(self, source_name: str, domain: str):
        self._source_name = source_name
        self.domain = domain
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    @property
    def source_name(self) -> str:
        return self._source_name

    @classmethod
    def _supports_location(cls, location: str) -> bool:
        location_normalized = (location or "").lower()
        return any(hint in location_normalized for hint in cls.GERMANY_HINTS)

    @staticmethod
    def _plain_text(value: str) -> str:
        return re.sub(r"\s+", " ", BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)).strip()

    def search(
        self,
        keywords: List[str],
        location: str,
        job_type: str = "all",
        seniority: str = "all",
        workplace_type: str = "all",
        date_posted: str = "all",
        limit_per_query: int = 25,
    ) -> List[UnifiedJob]:
        if not self._supports_location(location):
            return []

        results: List[UnifiedJob] = []
        seen: Set[str] = set()
        for keyword in keywords:
            query = f'site:{self.domain} "{keyword}" "{location}" job'
            try:
                response = self.session.get(self.SEARCH_URL + quote_plus(query), timeout=10)
                response.raise_for_status()
                root = ET.fromstring(response.content)
            except (requests.RequestException, ET.ParseError) as error:
                logger.warning("%s indexed search failed: %s", self.source_name, error)
                continue

            for item in root.findall(".//item")[:limit_per_query]:
                url = (item.findtext("link", default="") or "").strip()
                hostname = urlparse(url).netloc.lower()
                if not url or not (hostname == self.domain or hostname.endswith("." + self.domain)):
                    continue
                if url in seen:
                    continue

                title = self._plain_text(item.findtext("title", default=""))
                description = self._plain_text(item.findtext("description", default=""))[:700]
                if not title:
                    continue

                seen.add(url)
                job_id = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
                results.append(
                    UnifiedJob(
                        job_id=f"{self.domain}_{job_id}",
                        title=title,
                        company=self.source_name,
                        location=location,
                        url=url,
                        primary_application_url=url,
                        sources=[self.source_name],
                        posted_date="غير محدد",
                        description=description,
                        location_verified=True,
                        raw_source_data={"source": self.source_name, "keyword": keyword},
                    )
                )

        return results


class StepStoneSource(GermanJobBoardSource):
    def __init__(self):
        super().__init__("StepStone", "stepstone.de")


class BundesagenturSource(GermanJobBoardSource):
    def __init__(self):
        super().__init__("Bundesagentur für Arbeit", "arbeitsagentur.de")


class XingSource(GermanJobBoardSource):
    def __init__(self):
        super().__init__("XING Jobs", "xing.com")


class IndeedGermanySource(GermanJobBoardSource):
    def __init__(self):
        super().__init__("Indeed Deutschland", "de.indeed.com")


class MakeItGermanySource(GermanJobBoardSource):
    def __init__(self):
        super().__init__("Make it in Germany", "make-it-in-germany.com")
