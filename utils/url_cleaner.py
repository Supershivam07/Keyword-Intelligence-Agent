import requests
from urllib.parse import urlsplit, urlunsplit

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# Minimum content length to pass soft 404 check
# Pages shorter than this are likely homepages or error pages
MIN_CONTENT_LENGTH = 500


def remove_tracking_params(url: str) -> str:
    """
    Remove query parameters like ?utm=, ?ref=, ?bc=
    because they often cause redirects or 404 pages.
    """
    try:
        parts = urlsplit(url)
        clean_url = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
        return clean_url
    except Exception:
        return url


def resolve_redirect(url: str) -> str:
    """
    Resolve redirect URLs including Google/Vertex proxies.
    """
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=2,
            headers=HEADERS,
        )
        return response.url
    except Exception:
        return url


def is_valid_real_url(url: str) -> bool:
    """
    Remove vertex proxy links and invalid URLs.
    """
    if not url:
        return False

    if "vertexaisearch.cloud.google.com" in url:
        return False

    return url.startswith("http")


def _get_root_domain(url: str) -> str:
    """
    Extract root domain from a URL for soft 404 detection.
    e.g. https://techradar.com/article/best-llms → techradar.com
    """
    try:
        parts = urlsplit(url)
        return parts.netloc.lower().lstrip("www.")
    except Exception:
        return ""


def url_is_clean(url: str) -> tuple:
    """
    Strict URL validation with soft 404 detection.

    Returns (is_clean: bool, resolved_url: str)

    Checks:
    1. Must return HTTP 200
    2. Final URL after redirects must not have drifted to homepage
       (soft 404 detection — e.g. article deleted, redirected to root)
    3. Response content length must be above MIN_CONTENT_LENGTH
       (catches generic error pages that return 200)
    """
    try:
        response = requests.get(
            url,
            allow_redirects=True,
            timeout=4,
            headers=HEADERS,
        )

        # ── Check 1: Must be exactly 200 ──
        if response.status_code != 200:
            return False, url

        final_url = response.url

        # ── Check 2: Soft 404 — did URL drift to homepage? ──
        # If original path had depth (e.g. /article/something)
        # but final URL has no path or just "/" → redirected to homepage
        original_parts = urlsplit(url)
        final_parts    = urlsplit(final_url)

        original_path = original_parts.path.strip("/")
        final_path    = final_parts.path.strip("/")

        if original_path and not final_path:
            # Had a path before, now it's gone — soft 404
            return False, final_url

        # ── Check 3: Content length — catches generic error pages ──
        content = response.text
        if len(content) < MIN_CONTENT_LENGTH:
            return False, final_url

        return True, final_url

    except Exception:
        return False, url


def clean_urls_for_display(urls: list, target: int = 5) -> list:
    """
    Filter URLs strictly for display purposes only.
    Called AFTER Gemini analysis is complete.

    Steps:
    1. Remove vertexai links
    2. Remove tracking params
    3. Strict validation: 200 + soft 404 check + content length
    4. Deduplicate
    5. Backfill from remaining raw URLs if clean count < target
    6. Always return exactly `target` URLs

    NOTE: This is separate from clean_urls() which is used
    for the analysis pipeline. Do NOT replace clean_urls().
    """

    if not urls:
        return []

    # ── Pass 1: remove vertexai + tracking params ──
    sanitized = []
    for url in urls:
        if not isinstance(url, str):
            continue
        url = url.strip()
        if not is_valid_real_url(url):
            continue
        url = remove_tracking_params(url)
        sanitized.append(url)

    # ── Pass 2: strict validation ──
    clean    = []   # passed all checks
    fallback = []   # failed strict check but not vertexai
    seen     = set()

    for url in sanitized:
        if url in seen:
            continue
        seen.add(url)

        is_clean, resolved = url_is_clean(url)

        if is_clean:
            if resolved not in clean:
                clean.append(resolved)
        else:
            # keep as fallback in case we need to backfill
            if resolved not in fallback:
                fallback.append(resolved)

    # ── Pass 3: backfill to reach target count ──
    if len(clean) < target:
        for url in fallback:
            if url not in clean:
                clean.append(url)
            if len(clean) >= target:
                break

    # ── Always return exactly target URLs ──
    return clean[:target]


def clean_urls(urls, topic=None):
    """
    ORIGINAL clean_urls — used by analysis pipeline (run_step1, discover_topic).
    DO NOT change this function — it feeds URLs into Gemini for analysis.

    Steps:
    1. Remove tracking parameters
    2. Resolve redirects
    3. Remove vertex links
    4. Remove dead/404 pages
    5. Deduplicate
    6. Ensure up to 5 URLs returned
    """

    if not urls:
        return []

    cleaned = []
    fallback = []

    for url in urls:

        if not isinstance(url, str):
            continue

        url = url.strip()

        if not is_valid_real_url(url):
            continue

        # remove tracking parameters
        url = remove_tracking_params(url)

        resolved = resolve_redirect(url)

        # keep fallback list even if validation fails
        fallback.append(resolved)

        try:
            response = requests.get(
                resolved,
                allow_redirects=True,
                timeout=2,
                headers=HEADERS,
            )
            if response.status_code == 200:
                cleaned.append(resolved)
        except Exception:
            pass

    # deduplicate
    unique = []
    seen = set()

    for url in cleaned:
        if url not in seen:
            seen.add(url)
            unique.append(url)

    # if fewer than 5, backfill from fallback list
    if len(unique) < 5:
        for url in fallback:
            if url not in seen:
                seen.add(url)
                unique.append(url)
            if len(unique) >= 5:
                break

    return unique[:5]