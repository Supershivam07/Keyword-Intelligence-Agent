# ── Standard libs for JSON parsing and regex URL extraction
import json
import re
from typing import Dict, Any

# ── Gemini AI client for all LLM calls
from llm_clients.gemini_client import GeminiClient
# ── clean_urls: used in discover_topic pipeline | clean_urls_for_display: filters 404s for UI display
from utils.url_cleaner import clean_urls, clean_urls_for_display


class KeywordAgent:
    # ── Main agent class — runs 3-step SEO pipeline (URLs → Titles → Outline)

    # ── Initialize Gemini client on startup
    def __init__(self):
        self.gemini = GeminiClient()

    # ── Entry point for api.py and main.py — delegates to discover_topic
    def run(self, topic: str) -> Dict[str, Any]:
        return self.discover_topic(topic)

    # ── Parse Gemini response to JSON — tries direct parse first, then regex fallback
    # ── If Gemini wraps JSON in markdown or text, regex extracts the JSON block
    # ── Returns error dict if both attempts fail, so callers can check "error" key
    def _extract_json_safely(self, text: str) -> Dict[str, Any]:
        if not text:
            return {"error": "Empty response from model"}
        try:
            return json.loads(text)  # attempt 1: direct parse
        except Exception:
            pass
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)  # attempt 2: extract JSON block via regex
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass
        return {"error": "Model did not return valid JSON", "raw_output_preview": text[:500]}

    # ── Extract clean http URLs from raw Gemini output — strips emoji, punctuation
    # ── Gemini sometimes returns URLs mixed with bullet points or emojis — regex isolates the URL
    # ── Trailing punctuation like . , ) is stripped to avoid broken links
    def _sanitize_urls(self, urls):
        cleaned = []
        for url in urls:
            if not isinstance(url, str):
                continue
            url = url.strip()
            match = re.search(r"https?://[^\s<>\u2022🔥]+", url)  # match valid URL pattern
            if match:
                cleaned.append(match.group(0).rstrip(".,;:!?)"))  # strip trailing punctuation
        return cleaned

    # ── Generate titles + outline in one Gemini call — used only by discover_topic (api.py/main.py)
    def _generate_titles_and_outline(self, topic: str, urls: list):
        prompt = f"""
You are a professional SEO content strategist and blog architect.

TASK:
Analyze the top ranking pages and design an SEO-optimized blog structure.

TOPIC:
{topic}

TOP RANKING URLS:
{urls}

FIRST analyze these ranking pages carefully:

- Understand how the topic is structured
- Identify the main knowledge sections
- Identify subtopics used in those pages
- Determine how deeply the topic must be explained

Then generate:

1) 5 optimized SEO blog titles
2) A professional SEO blog outline

TITLE RULES:

- Generate EXACTLY 5 titles
- Titles must be unique
- Titles must sound natural and professional
- Titles should match patterns used by ranking pages
- Titles must be SEO optimized
- Do NOT generate H1 because titles already exist

OUTLINE RULES:

- DO NOT fix the number of sections
- Determine the number of H2 sections based on topic depth
- Usually generate between 3 and 8 H2 sections

CONTENT QUALITY RULES:

- Each H2 must represent a UNIQUE concept
- Avoid semantic duplication
- Do NOT repeat the same meaning using different wording
- Each section must expand the topic logically

H3 STRUCTURE RULES:

- Each H2 may contain between 2 and 4 H3 subsections
- H3 subsections must expand the idea of the parent H2
- H3 sections must NOT repeat ideas across different H2 sections
- Only include H3 when it improves explanation

GRAMMAR RULES:

- All headings must be grammatically correct
- Headings must read like professional blog headings
- Avoid awkward phrasing
- Avoid unnatural questions like:
  "What is type of AI agents"

SEO OPTIMIZATION RULES:

- Headings must include important SEO keywords naturally
- Headings should be informative and readable
- Headings should provide knowledge value for readers

OUTPUT RULES:

- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include any text outside JSON

JSON FORMAT:

{{
"title_suggestions": [
"title1",
"title2",
"title3",
"title4",
"title5"
],
"outline":[
{{"h2":"Section title","h3":["Subtopic","Subtopic","Subtopic"]}}
]
}}
"""
        try:
            response = self.gemini.generate(prompt)
            parsed = self._extract_json_safely(response)
            if "error" in parsed:
                return [], []
            return parsed.get("title_suggestions", []), parsed.get("outline", [])
        except Exception:
            return [], []

    # ── Step 1: Ask Gemini for top 10 ranking URLs + 15 SEO keywords — retries if insufficient
    def run_step1(self, topic: str) -> Dict[str, Any]:
        base_prompt = f"""
You are an elite SEO intelligence system.

TASK:

Simulate a real Google search for the topic below.

Identify the TOP 10 ranking URLs that appear on the FIRST PAGE
of Google search results for this topic.

These URLs must match what a user would see if they manually
searched the same topic on Google.

Then analyze those ranking pages to identify the SEO keywords
that help those pages rank.

CRITICAL OUTPUT RULES (VERY STRICT):

- Return EXACTLY 10 URLs from the first page of Google results
- URLs MUST be the exact ranking page (NOT homepage domains)
- URLs must directly discuss the topic
- Use the real article or topic page shown in Google
- Do NOT include vertexaisearch.cloud.google.com links
- You MUST return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include code fences
- Do NOT include any text before or after JSON

JSON FORMAT (STRICT):

{{
  "topic": "{topic}",
  "top_urls": [
    "url1","url2","url3","url4","url5",
    "url6","url7","url8","url9","url10"
  ],
  "high_ranking_keywords": [
    "kw1","kw2","kw3","kw4","kw5",
    "kw6","kw7","kw8","kw9","kw10",
    "kw11","kw12","kw13","kw14","kw15"
  ]
}}

TOPIC:
{topic}
"""
        retry_prompt = f"""
You FAILED to provide sufficient results.

Now strictly comply:

- Provide EXACTLY 10 real ranking URLs
- URLs MUST be the exact Google ranking pages
- URLs must NOT be homepage domains
- Avoid generic homepage URLs
- URLs must directly discuss the topic
- Provide Exactly 15 SEO keywords
- NO vertexaisearch.cloud.google.com links
- Return ONLY valid JSON
- No explanations
- No markdown
- No extra text

JSON FORMAT:

{{
  "topic": "{topic}",
  "top_urls": [
    "url1","url2","url3","url4","url5",
    "url6","url7","url8","url9","url10"
  ],
  "high_ranking_keywords": [
    "kw1","kw2","kw3","kw4","kw5",
    "kw6","kw7","kw8","kw9","kw10",
    "kw11","kw12","kw13","kw14","kw15"
  ]
}}

TOPIC:
{topic}
"""
        try:
            raw_response = self.gemini.generate(base_prompt)
            parsed = self._extract_json_safely(raw_response)
            if "error" in parsed:
                return parsed

            # ── Sanitize raw URLs from Gemini — removes emoji/punctuation artifacts
            raw_urls = self._sanitize_urls(parsed.get("top_urls", []))
            # ── Deduplicate keywords while preserving order
            keywords = list(dict.fromkeys(parsed.get("high_ranking_keywords", [])))

            if len(raw_urls) >= 5 and len(keywords) >= 10:
                # ── Keep raw_urls for Gemini analysis (step2/step3), show only clean 5 to user
                parsed["top_urls"]              = clean_urls_for_display(raw_urls, target=5)
                parsed["analysis_urls"]         = raw_urls
                parsed["high_ranking_keywords"] = keywords
                return parsed

            # ── Not enough data — retry with stricter prompt
            print("⚠️ Insufficient data in Step 1. Retrying...")
            raw_retry    = self.gemini.generate(retry_prompt)
            retry_parsed = self._extract_json_safely(raw_retry)

            if "error" in retry_parsed:
                # ── Retry also failed — return original result with best-effort display URLs
                parsed["top_urls"]              = clean_urls_for_display(raw_urls, target=5)
                parsed["analysis_urls"]         = raw_urls
                parsed["high_ranking_keywords"] = keywords
                return parsed

            retry_raw_urls = self._sanitize_urls(retry_parsed.get("top_urls", []))
            retry_keywords = list(dict.fromkeys(retry_parsed.get("high_ranking_keywords", [])))
            retry_parsed["top_urls"]              = clean_urls_for_display(retry_raw_urls, target=5)
            retry_parsed["analysis_urls"]         = retry_raw_urls
            retry_parsed["high_ranking_keywords"] = retry_keywords
            return retry_parsed

        except Exception as e:
            print(f"❌ Step 1 error: {e}")
            return {"error": "Step 1 failed", "exception": str(e)}

    # ── Step 2: Generate 5 SEO titles — uses selected keyword as reference if provided
    # ── Takes topic + analysis URLs from step1 + user-selected keyword
    # ── Returns {"title_suggestions": [...]} with exactly 5 titles
    def run_step2(self, topic: str, urls: list, selected_kw: str = "") -> Dict[str, Any]:
        # ── Build keyword reference block only if user selected a keyword — injected into prompt
        kw_reference_block = ""
        if selected_kw:
            kw_reference_block = f"""
USER SELECTED PRIMARY KEYWORD (VERY IMPORTANT — use as reference):

- Primary Keyword: {selected_kw}

All 5 titles MUST naturally include or be tightly aligned with this keyword.
The keyword should feel native in the title — not forced.
"""
        prompt = f"""
You are a professional SEO content strategist.

TASK:
Analyze the top ranking pages and generate 5 optimized SEO blog titles.

TOPIC:
{topic}

TOP RANKING URLS:
{urls}
{kw_reference_block}
TITLE RULES:

- Generate EXACTLY 5 titles
- Titles must be unique
- Titles must sound natural and professional
- Titles should match patterns used by ranking pages
- Titles must be SEO optimized
- At least 2 titles must include the exact topic keyword or a close variant
- At least 1 title must include a number (e.g. "Top 10", "7 Ways", "5 Best")
- Titles must match the search intent of the topic (informational, listicle, comparison, how-to)

STRONG OPENER RULES (VERY IMPORTANT):

- Do NOT start titles with vague or passive openers like:
  "Unlocking", "Exploring", "Understanding", "Navigating", "Discovering", "Diving Into"
- DO start titles with strong direct words like:
  "What Are", "How", "Best", "Top", "Complete Guide", "Why", a number, or the topic keyword itself
- Every title must give the reader an immediate clear reason to click
- Titles must feel like they belong on the first page of Google

GRAMMAR RULES:

- All titles must be grammatically correct
- Titles must read like professional blog headings
- Avoid awkward phrasing

OUTPUT RULES:

- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include any text outside JSON

JSON FORMAT:

{{
  "title_suggestions": [
    "title1",
    "title2",
    "title3",
    "title4",
    "title5"
  ]
}}
"""
        try:
            response = self.gemini.generate(prompt)
            parsed   = self._extract_json_safely(response)
            if "error" in parsed:
                return {"title_suggestions": []}
            return {"title_suggestions": parsed.get("title_suggestions", [])}
        except Exception as e:
            print(f"❌ Step 2 error: {e}")
            return {"error": "Step 2 failed", "exception": str(e)}

    # ── Step 3: Generate SEO blog outline — anchored to selected title + keyword if provided
    # ── Takes topic + analysis URLs from step1 + user-selected title and keyword
    # ── Detects topic type (listicle/guide/how-to/comparison) and structures H2s accordingly
    # ── Returns {"outline": [{"h2": "...", "h3": [...]}]}
    def run_step3(self, topic: str, urls: list, selected_title: str = "", selected_kw: str = "") -> Dict[str, Any]:
        # ── Build user input block only if user made selections — injected into prompt as primary reference
        user_input_block = ""
        if selected_title or selected_kw:
            user_input_block = f"""
USER SELECTED INPUTS (VERY IMPORTANT — use these as your primary reference):

- Selected Title: {selected_title if selected_title else "Not provided"}
- Selected Primary Keyword: {selected_kw if selected_kw else "Not provided"}

These inputs were chosen by the user from AI suggestions.
The outline MUST be tightly aligned with this title and keyword.
Every H2 and H3 must serve the intent of this title and keyword.
Do NOT go off-topic or generate sections unrelated to this focus.
"""
        prompt = f"""
You are a professional SEO blog architect.

TASK:
Analyze the top ranking pages and design a professional SEO blog outline.

TOPIC:
{topic}

TOP RANKING URLS:
{urls}
{user_input_block}

TOPIC TYPE DETECTION (DO THIS FIRST):

Before writing the outline, detect the topic type:

- LISTICLE: topic contains "Top", "Best", "10", numbers, or ranking intent
  → H2s must be direct ranked sections like "Top 10 X Ranked", "Best X for Y", "X vs Y Compared"
  → Avoid vague H2 openers — every H2 must sound like a ranking or comparison

- GUIDE / EXPLAINER: topic is a concept, definition, or "how it works"
  → H2s must flow logically: Definition → How it Works → Types → Use Cases → Benefits → Future
  → Each H2 must expand knowledge progressively

- HOW-TO: topic starts with "How to" or implies steps
  → H2s must be clear action steps in logical order
  → Use numbered or sequential language where appropriate

- COMPARISON: topic compares two or more things
  → H2s must cover each subject individually then compare directly

OUTLINE RULES:

- DO NOT fix the number of sections
- Determine the number of H2 sections based on topic depth and type
- Usually generate between 3 and 8 H2 sections

STRONG H2 OPENER RULES (VERY IMPORTANT):

- Do NOT start H2s with vague openers like:
  "Navigating", "Exploring", "Understanding", "Discovering", "Unlocking", "Delving Into"
- Every H2 must be direct, specific, and immediately informative
- H2s must match the topic type detected above

CONTENT QUALITY RULES:

- Each H2 must represent a UNIQUE concept
- Avoid semantic duplication
- Do NOT repeat the same meaning using different wording
- Each section must expand the topic logically

H3 STRUCTURE RULES:

- Each H2 may contain between 2 and 4 H3 subsections
- H3 subsections must expand the idea of the parent H2
- H3 sections must NOT repeat ideas across different H2 sections
- Only include H3 when it improves explanation

GRAMMAR RULES:

- All headings must be grammatically correct
- Headings must read like professional blog headings
- Avoid awkward phrasing

SEO OPTIMIZATION RULES:

- Headings must include important SEO keywords naturally
- Headings should be informative and readable
- Headings should provide knowledge value for readers

OUTPUT RULES:

- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include any text outside JSON

JSON FORMAT:

{{
  "outline": [
    {{"h2": "Section title", "h3": ["Subtopic", "Subtopic", "Subtopic"]}}
  ]
}}
"""
        try:
            response = self.gemini.generate(prompt)
            parsed   = self._extract_json_safely(response)
            if "error" in parsed:
                return {"outline": []}
            return {"outline": parsed.get("outline", [])}
        except Exception as e:
            print(f"❌ Step 3 error: {e}")
            return {"error": "Step 3 failed", "exception": str(e)}

    # ── Full pipeline in one call — fetches URLs, keywords, titles, outline (used by api.py + main.py)
    def discover_topic(self, topic: str) -> Dict[str, Any]:
        print("[Agent] Searching and analyzing top-ranking pages...")

        base_prompt = f"""
You are an elite SEO intelligence system.

TASK:

Simulate a real Google search for the topic below.

Identify the TOP 10 ranking URLs that appear on the FIRST PAGE
of Google search results for this topic.

These URLs must match what a user would see if they manually
searched the same topic on Google.

Then analyze those ranking pages to identify the SEO keywords
that help those pages rank.

CRITICAL OUTPUT RULES (VERY STRICT):

- Return EXACTLY 10 URLs from the first page of Google results
- URLs MUST be the exact ranking page (NOT homepage domains)
- URLs must directly discuss the topic
- Use the real article or topic page shown in Google
- Do NOT include vertexaisearch.cloud.google.com links
- You MUST return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include code fences
- Do NOT include any text before or after JSON

JSON FORMAT (STRICT):

{{
  "topic": "{topic}",
  "top_urls": [
    "url1","url2","url3","url4","url5",
    "url6","url7","url8","url9","url10"
  ],
  "high_ranking_keywords": [
    "kw1","kw2","kw3","kw4","kw5",
    "kw6","kw7","kw8","kw9","kw10",
    "kw11","kw12","kw13","kw14","kw15"
  ]
}}

TOPIC:
{topic}
"""
        retry_prompt = f"""
You FAILED to provide sufficient results.

Now strictly comply:

- Provide EXACTLY 10 real ranking URLs
- URLs MUST be the exact Google ranking pages
- URLs must NOT be homepage domains
- Avoid generic homepage URLs
- URLs must directly discuss the topic
- Provide Exactly 15 SEO keywords
- NO vertexaisearch.cloud.google.com links
- Return ONLY valid JSON
- No explanations
- No markdown
- No extra text

JSON FORMAT:

{{
  "topic": "{topic}",
  "top_urls": [
    "url1","url2","url3","url4","url5",
    "url6","url7","url8","url9","url10"
  ],
  "high_ranking_keywords": [
    "kw1","kw2","kw3","kw4","kw5",
    "kw6","kw7","kw8","kw9","kw10",
    "kw11","kw12","kw13","kw14","kw15"
  ]
}}

TOPIC:
{topic}
"""
        try:
            raw_response = self.gemini.generate(base_prompt)
            parsed = self._extract_json_safely(raw_response)

            if "error" in parsed:
                print("⚠️ Raw Gemini output (non-JSON):")
                print(raw_response[:500])
                return parsed

            # ── Sanitize + clean URLs — remove trackers, resolve redirects, verify alive
            urls     = self._sanitize_urls(parsed.get("top_urls", []))
            urls     = clean_urls(urls, topic)
            # ── Deduplicate keywords while preserving order
            keywords = list(dict.fromkeys(parsed.get("high_ranking_keywords", [])))
            parsed["top_urls"]              = urls
            parsed["high_ranking_keywords"] = keywords

            if len(urls) >= 5 and len(keywords) >= 10:
                # ── Enough data — generate titles + outline in one Gemini call
                titles, outline = self._generate_titles_and_outline(topic, urls)
                parsed["title_suggestions"] = titles
                parsed["outline"]           = outline
                return parsed

            # ── Not enough data — retry with stricter prompt
            print("⚠️ Insufficient data. Retrying with stricter enforcement...")
            raw_retry    = self.gemini.generate(retry_prompt)
            retry_parsed = self._extract_json_safely(raw_retry)

            if "error" in retry_parsed:
                return parsed  # return original if retry also fails

            retry_urls     = self._sanitize_urls(retry_parsed.get("top_urls", []))
            retry_urls     = clean_urls(retry_urls, topic)
            retry_keywords = list(dict.fromkeys(retry_parsed.get("high_ranking_keywords", [])))
            retry_parsed["top_urls"]              = retry_urls
            retry_parsed["high_ranking_keywords"] = retry_keywords

            # ── Generate titles + outline from retry data
            titles, outline = self._generate_titles_and_outline(topic, retry_urls)
            retry_parsed["title_suggestions"] = titles
            retry_parsed["outline"]           = outline
            return retry_parsed

        except Exception as e:
            print(f"❌ Gemini search error: {e}")
            return {"error": "Gemini search generation failed", "exception": str(e)}