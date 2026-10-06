"""Recruiter-hiring lead discovery for public LinkedIn post URLs.

LinkedIn content search requires a signed-in LinkedIn session.  To preserve the
app's no-login design, this source searches a public web index for LinkedIn
post URLs. Results are leads, not direct application listings.
"""

import hashlib
import logging
import re
from typing import List, Optional, Set
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

from .base import BaseJobSource, UnifiedJob

logger = logging.getLogger(__name__)


class LinkedInRecruiterPostSource(BaseJobSource):
    """Find public LinkedIn recruiter posts through Bing's RSS endpoint."""

    RSS_URL = "https://www.bing.com/search?format=rss&q="
    HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WaslaJobDiscovery/1.0)"}

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(self.HEADERS)

    @property
    def source_name(self) -> str:
        return "LinkedIn Recruiter Posts"

    @staticmethod
    def _clean(text: str) -> str:
        return re.sub(r"\s+", " ", BeautifulSoup(text or "", "html.parser").get_text(" ", strip=True)).strip()

    @staticmethod
    def _location_is_mentioned(text: str, location: str) -> bool:
        text = text.lower()
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
        for keyword in keywords:
            query_variants = [
                f'site:linkedin.com/posts ("we are hiring" OR "we\'re hiring" OR "hiring") "{keyword}" "{location}"',
                f'site:linkedin.com/posts "{keyword}" ("{location}" OR UAE OR Dubai) (vacancy OR opportunity OR recruitment)',
                f'site:linkedin.com/posts "{keyword}" ("immediate joining" OR "urgent hiring" OR "open position") "{location}"',
            ]
            for query in query_variants:
                try:
                    response = self.session.get(self.RSS_URL + quote_plus(query), timeout=10)
                    if response.status_code != 200:
                        logger.warning("Recruiter-post search returned %s", response.status_code)
                        continue
                    root = ET.fromstring(response.content)
                    for item in root.findall(".//item")[:limit_per_query]:
                        link = self._clean(item.findtext("link", default=""))
                        if "linkedin.com/posts" not in link.lower():
                            continue
                        key = hashlib.sha256(link.encode("utf-8")).hexdigest()[:16]
                        if key in seen:
                            continue
                        headline = self._clean(item.findtext("title", default=""))
                        description = self._clean(item.findtext("description", default=""))[:900]
                        location_verified = self._location_is_mentioned(f"{headline} {description}", location)
                        if not location_verified:
                            continue
                        seen.add(key)
                        pub_date = self._clean(item.findtext("pubDate", default="")) or "Unknown"
                        results.append(UnifiedJob(
                        job_id=f"linkedin_post_{key}",
                        title=f"Recruiter post: {keyword}",
                        company="LinkedIn recruiter post",
                        location=location,
                        url=link,
                        primary_application_url=link,
                        sources=["LinkedIn Recruiter Posts"],
                        posted_date=pub_date,
                        description=f"{headline}. {description}".strip(), location_verified=True,
                        raw_source_data={"source": "LinkedIn Recruiter Posts", "keyword": keyword, "lead": True},
                        ))
                except (requests.RequestException, ET.ParseError) as error:
                    logger.warning("Recruiter-post search failed: %s", error)
        return results
