"""Indeed public search adapter.

The public HTML may occasionally challenge automated traffic.  This adapter is
intentionally fault-isolated so an Indeed block never breaks other sources.
"""

import logging
import re
import hashlib
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

from .base import BaseJobSource, UnifiedJob

logger = logging.getLogger(__name__)


class IndeedSource(BaseJobSource):
    """Discover listings from Indeed's public regional search pages."""

    BASE_URLS = {
        "uae": "https://ae.indeed.com/jobs",
        "united arab emirates": "https://ae.indeed.com/jobs",
        "dubai": "https://ae.indeed.com/jobs",
        "abu dhabi": "https://ae.indeed.com/jobs",
        "egypt": "https://eg.indeed.com/jobs",
        "cairo": "https://eg.indeed.com/jobs",
        "saudi": "https://sa.indeed.com/jobs",
        "saudi arabia": "https://sa.indeed.com/jobs",
        "riyadh": "https://sa.indeed.com/jobs",
        "qatar": "https://qa.indeed.com/jobs",
        "doha": "https://qa.indeed.com/jobs",
        "al rayyan": "https://qa.indeed.com/jobs",
        "germany": "https://de.indeed.com/jobs",
        "berlin": "https://de.indeed.com/jobs",
        "munich": "https://de.indeed.com/jobs",
        "hamburg": "https://de.indeed.com/jobs",
        "frankfurt": "https://de.indeed.com/jobs",
        "netherlands": "https://nl.indeed.com/jobs",
        "amsterdam": "https://nl.indeed.com/jobs",
        "rotterdam": "https://nl.indeed.com/jobs",
        "the hague": "https://nl.indeed.com/jobs",
        "utrecht": "https://nl.indeed.com/jobs",
    }
    DEFAULT_URL = "https://www.indeed.com/jobs"
    DATE_MAP = {"past_24h": "1", "past_week": "7", "past_month": "30"}
    BING_RSS_URL = "https://www.bing.com/search?format=rss&q="
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
    }

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(self.HEADERS)

    @property
    def source_name(self) -> str:
        return "Indeed"

    def _base_url(self, location: str) -> str:
        normalized = location.lower()
        for key, url in self.BASE_URLS.items():
            if key in normalized:
                return url
        return self.DEFAULT_URL

    def _bing_fallback(self, keyword: str, location: str, base_url: str, limit: int) -> List[UnifiedJob]:
        """Use public search indexing when Indeed challenges its HTML page."""
        domain = base_url.split("//", 1)[-1].split("/", 1)[0]
        query = f'site:{domain}/viewjob "{keyword}" "{location}"'
        try:
            response = self.session.get(self.BING_RSS_URL + quote_plus(query), timeout=10)
            response.raise_for_status()
            root = ET.fromstring(response.content)
        except (requests.RequestException, ET.ParseError) as error:
            logger.warning("Indeed indexed-search fallback failed: %s", error)
            return []

        results: List[UnifiedJob] = []
        for item in root.findall(".//item")[:limit]:
            url = item.findtext("link", default="").strip()
            if "indeed." not in url.lower():
                continue
            headline = self._text(BeautifulSoup(item.findtext("title", default=""), "html.parser"))
            description = self._text(BeautifulSoup(item.findtext("description", default=""), "html.parser"))[:700]
            if not headline:
                continue
            job_key = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
            searchable = f"{headline} {description}".lower()
            location_verified = self._location_is_mentioned(searchable, location)
            results.append(UnifiedJob(
                job_id=f"indeed_indexed_{job_key}", title=headline, company="Indeed listing",
                location=location if location_verified else "Unknown", url=url, primary_application_url=url, sources=["Indeed"],
                posted_date=self._text(BeautifulSoup(item.findtext("pubDate", default=""), "html.parser")) or "Unknown",
                description=description, location_verified=location_verified,
                raw_source_data={"source": "Indeed (indexed)", "keyword": keyword},
            ))
        return results

    @staticmethod
    def _text(element) -> str:
        return re.sub(r"\s+", " ", element.get_text(" ", strip=True) if element else "").strip()

    @staticmethod
    def _location_is_mentioned(text: str, location: str) -> bool:
        aliases = {
            "united arab emirates": ("uae", "united arab emirates", "dubai", "abu dhabi", "sharjah"),
            "dubai": ("dubai",), "abu dhabi": ("abu dhabi",), "cairo": ("cairo",),
            "egypt": ("egypt", "cairo"), "riyadh": ("riyadh",), "saudi arabia": ("saudi", "riyadh", "jeddah"),
            "qatar": ("qatar", "doha"), "doha": ("doha",),
            "germany": ("germany", "berlin", "munich", "hamburg", "frankfurt"), "berlin": ("berlin",), "munich": ("munich",),
            "netherlands": ("netherlands", "amsterdam", "rotterdam", "the hague", "utrecht"), "amsterdam": ("amsterdam",), "rotterdam": ("rotterdam",),
        }
        target = location.lower()
        return any(any(alias in text for alias in values) for key, values in aliases.items() if key in target)

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
        results: List[UnifiedJob] = []
        seen: Set[str] = set()
        pages = max(1, min((limit_per_query + 9) // 10, 2))
        base_url = self._base_url(location)

        for keyword in keywords:
            found_for_keyword = 0
            for page in range(pages):
                params: Dict[str, str] = {"q": keyword, "l": location, "start": str(page * 10)}
                if date_posted in self.DATE_MAP:
                    params["fromage"] = self.DATE_MAP[date_posted]
                try:
                    response = self.session.get(base_url, params=params, timeout=10)
                    if response.status_code != 200:
                        logger.warning("Indeed returned %s for %r", response.status_code, keyword)
                        break
                    soup = BeautifulSoup(response.content, "html.parser")
                    cards = soup.select(".job_seen_beacon, .jobsearch-ResultsList > li, div[data-jk]")
                    if not cards:
                        break
                    for card in cards:
                        link = card.select_one("a.jcs-JobTitle[href], h2 a[href], a[data-jk][href]")
                        title = self._text(link) or self._text(card.select_one("h2"))
                        if not link or not title:
                            continue
                        job_key = card.get("data-jk") or link.get("data-jk") or link.get("href", "")
                        job_key = re.sub(r"[^a-zA-Z0-9]", "", job_key)[-32:]
                        if not job_key or job_key in seen:
                            continue
                        seen.add(job_key)
                        company = self._text(card.select_one("[data-testid='company-name'], .companyName")) or "Unknown company"
                        location_element = card.select_one("[data-testid='text-location'], .companyLocation")
                        job_location = self._text(location_element) or "Unknown"
                        date = self._text(card.select_one("[data-testid='myJobsStateDate'], .date")) or "Unknown"
                        snippet = self._text(card.select_one(".job-snippet, .underShelfFooter"))[:700]
                        url = urljoin(base_url, link.get("href", ""))
                        results.append(UnifiedJob(
                            job_id=f"indeed_{job_key}", title=title, company=company,
                            location=job_location, url=url, primary_application_url=url,
                            sources=["Indeed"], posted_date=date, description=snippet,
                            location_verified=bool(location_element),
                            raw_source_data={"source": "Indeed", "keyword": keyword},
                        ))
                        found_for_keyword += 1
                except requests.RequestException as error:
                    logger.warning("Indeed request failed: %s", error)
                    break
            if not found_for_keyword:
                results.extend(self._bing_fallback(keyword, location, base_url, limit_per_query))
        return results
