import time
import json
import re
from typing import Dict, Any

from llm_clients.gemini_client import GeminiClient
from llm_clients.glm_client import GLMClient
from utils.url_cleaner import clean_urls


class MultiLLMKeywordAgent:
    """
    Minimal Multi-LLM SEO Agent

    GLM → Topic normalization
    Gemini → Search + SEO analysis
    Python → Cleaning + validation
    """

    def __init__(self):
        self.gemini = GeminiClient()
        self.glm = GLMClient()

    # =========================================================
    # GLM Topic Normalization
    # =========================================================

    def normalize_topic(self, topic: str) -> str:

        prompt = f"""
Normalize the following topic for SEO analysis.

RULES:
- Return ONLY the cleaned topic text
- Do NOT explain anything
- Do NOT add extra words

Topic:
{topic}
"""

        try:
            result = self.glm.reason(prompt)
            return result.strip()

        except Exception:
            return topic

    # =========================================================
    # Safe JSON Extraction
    # =========================================================

    def extract_json(self, text: str):

        try:
            return json.loads(text)
        except Exception:
            pass

        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
        except Exception:
            pass

        return None

    # =========================================================
    # Gemini Call with Retry (503 protection)
    # =========================================================

    def gemini_call(self, prompt: str):

        retries = 3

        for attempt in range(retries):

            try:
                return self.gemini.generate(prompt)

            except Exception as e:

                if "503" in str(e) and attempt < retries - 1:
                    print("⚠ Gemini overloaded — retrying...")
                    time.sleep(3)
                    continue

                raise

    # =========================================================
    # MAIN PIPELINE
    # =========================================================

    def run(self, topic: str) -> Dict[str, Any]:

        print("[Multi-LLM Agent] Starting pipeline...")

        start_time = time.time()

        # -----------------------------
        # Step 1 — GLM Topic Normalization
        # -----------------------------

        clean_topic = self.normalize_topic(topic)

        print("[GLM] Clean topic:", clean_topic)

        # -----------------------------
        # Step 2 — Gemini SEO Analysis
        # -----------------------------

        prompt = f"""
You are an elite SEO intelligence system.

TASK:
Analyze the topic and identify the highest-ranking SEO keywords
based ONLY on real top-ranking web pages.

CRITICAL OUTPUT RULES (VERY STRICT):

- You MUST return ONLY valid JSON
- Do NOT include explanations
- Do NOT include markdown
- Do NOT include code fences
- Minimum 5 URLs required
- Minimum 10 keywords required
- URLs must be real authoritative ranking pages

JSON FORMAT (STRICT):

{{
  "topic": "{clean_topic}",
  "top_urls": ["url1", "url2", "url3", "url4", "url5"],
  "high_ranking_keywords": ["kw1", "kw2", "kw3", "kw4", "kw5", "kw6", "kw7", "kw8", "kw9", "kw10"]
}}

TOPIC:
{clean_topic}
"""

        raw_response = self.gemini_call(prompt)

        parsed = self.extract_json(raw_response)

        if not parsed:

            return {
                "error": "Invalid JSON from Gemini",
                "raw_output_preview": raw_response[:500],
            }

        # -----------------------------
        # Step 3 — Python Cleaning
        # -----------------------------

        urls = clean_urls(parsed.get("top_urls", []))

        keywords = list(dict.fromkeys(parsed.get("high_ranking_keywords", [])))

        # -----------------------------
        # Validation Retry
        # -----------------------------

        if len(urls) < 5 or len(keywords) < 10:

            print("⚠ Insufficient results — retrying...")

            raw_retry = self.gemini_call(prompt)

            retry_parsed = self.extract_json(raw_retry)

            if retry_parsed:

                urls = clean_urls(retry_parsed.get("top_urls", []))

                keywords = list(
                    dict.fromkeys(retry_parsed.get("high_ranking_keywords", []))
                )

        result = {
            "topic": clean_topic,
            "top_urls": urls,
            "high_ranking_keywords": keywords,
        }

        end_time = time.time()

        print(
            "[Multi-LLM Agent] Completed in",
            round(end_time - start_time, 2),
            "seconds",
        )

        return result