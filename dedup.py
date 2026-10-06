import difflib
import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sources.base import UnifiedJob

logger = logging.getLogger(__name__)


class JobDeduplicator:
    """Multi-Signal, conservative deduplication engine for job opportunities."""


    LEGAL_SUFFIXES = [
        r"\bincorporated\b",
        r"\bcorporation\b",
        r"\bcorp\.?\b",
        r"\binc\.?\b",
        r"\bllc\.?\b",
        r"\bltd\.?\b",
        r"\blimited\b",
        r"\bco\.\b",
        r"\bco\b(?!\w)",
        r"\bش\.م\.م\b",
        r"\bذ\.م\.م\b",
    ]

    @classmethod
    def normalize_company(cls, name: str) -> str:
        """Conservatively normalize company name by removing ONLY pure legal suffixes."""
        if not name:
            return ""
        norm = name.strip().lower()

        norm = re.sub(r"[^\w\s\u0600-\u06FF]", " ", norm)
        for pat in cls.LEGAL_SUFFIXES:
            norm = re.sub(pat, " ", norm, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", norm).strip()

    @classmethod
    def normalize_title_tokens(cls, title: str) -> List[str]:
        """Extract clean alphanumeric tokens from title."""
        if not title:
            return []
        cleaned = re.sub(r"[^\w\s\u0600-\u06FF]", " ", title.lower())
        tokens = [t for t in cleaned.split() if len(t) > 1]
        return tokens

    @classmethod
    def calculate_title_similarity(cls, title1: str, title2: str) -> float:
        """Calculate token-based and sequence-based title similarity ratio."""
        t1_clean = re.sub(r"\s+", " ", re.sub(r"[^\w\s\u0600-\u06FF]", " ", title1.lower())).strip()
        t2_clean = re.sub(r"\s+", " ", re.sub(r"[^\w\s\u0600-\u06FF]", " ", title2.lower())).strip()

        if t1_clean == t2_clean:
            return 1.0


        seq_ratio = difflib.SequenceMatcher(None, t1_clean, t2_clean).ratio()


        tokens1 = set(cls.normalize_title_tokens(title1))
        tokens2 = set(cls.normalize_title_tokens(title2))
        if not tokens1 or not tokens2:
            return seq_ratio

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        jaccard = len(intersection) / len(union)


        combined = (jaccard * 0.60) + (seq_ratio * 0.40)
        return combined

    @classmethod
    def canonicalize_url(cls, url: str) -> str:
        """Strip tracking parameters, query tokens, and fragments from URL."""
        if not url or url.startswith("#"):
            return ""
        try:
            parsed = urlparse(url)

            query_params = parse_qs(parsed.query)
            clean_params = {
                k: v for k, v in query_params.items()
                if not any(k.lower().startswith(prefix) for prefix in [
                    "utm_", "ref", "trk", "tracking", "source", "feed", "original_referer"
                ])
            }
            clean_query = urlencode(clean_params, doseq=True)
            clean_path = parsed.path.rstrip("/")
            canonical = urlunparse((
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                clean_path,
                "",
                clean_query,
                "",
            ))
            return canonical
        except Exception:
            return url.split("?")[0].rstrip("/").lower()

    @classmethod
    def extract_core_location(cls, loc: str) -> str:
        """Extract core city or normalized location keyword."""
        loc_clean = loc.lower()
        if any(c in loc_clean for c in ["cairo", "القاهرة"]):
            return "cairo"
        if any(c in loc_clean for c in ["alexandria", "الإسكندرية", "alex"]):
            return "alexandria"
        if any(c in loc_clean for c in ["giza", "الجيزة"]):
            return "giza"
        if any(c in loc_clean for c in ["mansoura", "المنصورة"]):
            return "mansoura"
        if any(c in loc_clean for c in ["riyadh", "الرياض"]):
            return "riyadh"
        if any(c in loc_clean for c in ["dubai", "دبي"]):
            return "dubai"
        if any(c in loc_clean for c in ["remote", "عن بُعد", "worldwide", "anywhere"]):
            return "remote"

        return re.sub(r"[^\w\u0600-\u06FF]", "", loc_clean)

    @classmethod
    def is_location_compatible(cls, loc1: str, loc2: str) -> bool:
        """Check if two job locations are compatible or contradictory."""
        core1 = cls.extract_core_location(loc1)
        core2 = cls.extract_core_location(loc2)


        if core1 == "remote" or core2 == "remote":
            return True
        if not core1 or not core2:
            return True


        known_cities = {"cairo", "alexandria", "giza", "mansoura", "riyadh", "dubai"}
        if core1 in known_cities and core2 in known_cities:
            return core1 == core2


        if core1 == "egypt" or core2 == "egypt":
            return True

        return core1 == core2

    @classmethod
    def is_duplicate(cls, job1: UnifiedJob, job2: UnifiedJob) -> Tuple[bool, float, str]:
        """
        Determine if two jobs are duplicates using multi-signal evaluation.
        Returns: (is_dup, confidence_score, reason)
        """

        url1 = cls.canonicalize_url(job1.url)
        url2 = cls.canonicalize_url(job2.url)
        if url1 and url2 and url1 == url2:
            return True, 1.0, "identical_canonical_url"


        comp1 = cls.normalize_company(job1.company)
        comp2 = cls.normalize_company(job2.company)
        if not comp1 or not comp2 or comp1 != comp2:

            return False, 0.0, "different_companies"


        if not cls.is_location_compatible(job1.location, job2.location):

            return False, 0.0, "contradictory_locations"


        title_sim = cls.calculate_title_similarity(job1.title, job2.title)
        if title_sim < 0.82:

            return False, title_sim, "low_title_similarity"


        if job1.description and job2.description and len(job1.description) > 50 and len(job2.description) > 50:
            words1 = set(job1.description.lower().split()[:60])
            words2 = set(job2.description.lower().split()[:60])
            desc_jaccard = len(words1.intersection(words2)) / max(len(words1.union(words2)), 1)

            if desc_jaccard < 0.15:
                return False, desc_jaccard, "contradictory_descriptions"


        confidence = 0.5 * 1.0 + 0.3 * title_sim + 0.2 * (1.0 if cls.extract_core_location(job1.location) == cls.extract_core_location(job2.location) else 0.7)
        if confidence >= 0.85:
            return True, confidence, f"multi_signal_match (confidence={confidence:.2f})"

        return False, confidence, f"insufficient_confidence ({confidence:.2f})"

    @classmethod
    def merge_jobs(cls, primary: UnifiedJob, duplicate: UnifiedJob) -> UnifiedJob:
        """Merge duplicate job into primary job, retaining all sources and best apply link."""
        merged_sources = list(dict.fromkeys(primary.sources + duplicate.sources))


        best_url = primary.primary_application_url or primary.url
        if "tanqeeb.com" in (duplicate.primary_application_url or "") and "linkedin.com" in best_url:
            best_url = duplicate.primary_application_url or duplicate.url


        best_desc = primary.description if len(primary.description) >= len(duplicate.description) else duplicate.description


        best_loc = primary.location if len(primary.location) >= len(duplicate.location) else duplicate.location
        if primary.posted_date in ["غير محدد", "·", "", None] and duplicate.posted_date not in ["غير محدد", "·", "", None]:
            primary.posted_date = duplicate.posted_date

        primary.sources = merged_sources
        primary.primary_application_url = best_url
        primary.description = best_desc
        primary.location = best_loc
        primary.eligibility_note = primary.eligibility_note or duplicate.eligibility_note
        primary.location_verified = primary.location_verified and duplicate.location_verified
        primary.relevance_score = max(primary.relevance_score, duplicate.relevance_score)

        return primary

    @classmethod
    def deduplicate_jobs(cls, jobs: List[UnifiedJob]) -> Tuple[List[UnifiedJob], int]:
        """
        Deduplicate a list of jobs using conservative multi-signal analysis.
        Returns (unique_jobs, duplicates_merged_count).
        """
        unique_jobs: List[UnifiedJob] = []
        company_buckets: Dict[str, List[UnifiedJob]] = {}
        url_index: Dict[str, UnifiedJob] = {}
        duplicates_count = 0

        for candidate in jobs:
            merged = False
            candidate_url = cls.canonicalize_url(candidate.url)
            url_match = url_index.get(candidate_url) if candidate_url else None
            candidates = [url_match] if url_match else company_buckets.get(cls.normalize_company(candidate.company), [])
            for existing in candidates:
                if existing is None:
                    continue
                is_dup, score, reason = cls.is_duplicate(existing, candidate)
                if is_dup:
                    cls.merge_jobs(existing, candidate)
                    duplicates_count += 1
                    merged = True
                    logger.debug(f"Merged duplicate: '{candidate.title}' into '{existing.title}' via {reason}")
                    break

            if not merged:
                unique_jobs.append(candidate)
                company_buckets.setdefault(cls.normalize_company(candidate.company), []).append(candidate)
                canonical_url = cls.canonicalize_url(candidate.url)
                if canonical_url:
                    url_index[canonical_url] = candidate

        return unique_jobs, duplicates_count
