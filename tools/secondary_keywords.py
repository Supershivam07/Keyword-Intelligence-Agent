# tools/secondary_keywords.py
from typing import List, Dict, Any
from llm_clients.gemini_client import GeminiClient


def generate_secondary_keywords(primary_keywords: List[str], topic: str) -> Dict[str, Any]:
    """
    Lazily create the GeminiClient (no client at import time).
    Returns JSON-like dict with secondary keywords.
    """
    gemini = GeminiClient()

    prompt = f"""
You are an advanced semantic SEO optimizer.

Generate SECONDARY supporting keywords that improve topical authority.

STRICT RULES:

- Must be semantically related to primary keywords
- Include long-tail variations
- Include NLP/semantic variations
- Avoid duplicates
- Avoid repeating primary keywords
- Focus on topical depth

Return ONLY JSON:

{{
  "secondary_keywords": [
    {{
      "keyword": "example long tail keyword",
      "type": "long-tail"
    }}
  ]
}}

Primary Keywords: {primary_keywords}
Topic: {topic}
"""

    return gemini.generate_json(prompt)
