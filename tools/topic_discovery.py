from llm_clients.gemini_client import GeminiClient
from utils.url_cleaner import clean_urls


MIN_REQUIRED_URLS = 5
MAX_FETCH = 10


def _fetch_from_gemini(topic: str) -> dict:
    """
    Single Gemini search call.
    """
    gemini = GeminiClient()

    prompt = f"""
You are an expert SEO keyword analyst.

TASK:

1. Search Google for the topic: "{topic}"
2. Identify the top {MAX_FETCH} ranking websites
3. Analyze those pages deeply
4. Extract high-ranking SEO keywords

RETURN STRICT JSON FORMAT:

{{
  "topic": "{topic}",
  "top_urls": ["url1", "url2"],
  "high_ranking_keywords": ["keyword1", "keyword2"]
}}

IMPORTANT:

- Use real high-ranking websites
- Focus on SEO-driving keywords
- Prefer authoritative domains
- Avoid duplicates
- JSON only
"""

    return gemini.generate_json_with_search(prompt)


def discover_topic(topic: str):
    """
    Robust topic discovery with SERP backfill.
    Guarantees minimum clean URLs when possible.
    """

    # 🔹 First fetch
    result = _fetch_from_gemini(topic)

    if "error" in result:
        return result

    raw_urls = result.get("top_urls", [])
    clean = clean_urls(raw_urls)

    # 🔥 BACKFILL LOGIC (mentor-safe)
    if len(clean) < MIN_REQUIRED_URLS:
        print(f"⚠️ Only {len(clean)} clean URLs found. Backfilling...")

        retry_result = _fetch_from_gemini(topic)

        if "error" not in retry_result:
            retry_urls = retry_result.get("top_urls", [])
            merged = clean + clean_urls(retry_urls)

            # deduplicate
            seen = set()
            final_urls = []

            for url in merged:
                if url not in seen:
                    seen.add(url)
                    final_urls.append(url)

            clean = final_urls

    # ✅ enforce top 5 clean URLs
    clean = clean[:MIN_REQUIRED_URLS]

    return {
        "topic": topic,
        "top_urls": clean,
        "high_ranking_keywords": result.get("high_ranking_keywords", []),
    }