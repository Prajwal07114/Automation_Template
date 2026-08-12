"""
Prompt construction for the LLM call.

Kept isolated so the wording can be iterated on without touching
generator.py's request/retry logic.
"""

import json
from models import NewsletterContent

# A trimmed example of the exact shape we want back, used to anchor the model.
_EXAMPLE_SCHEMA = {
    "category": "Travel Insurance",
    "audience": "Indian travelers going abroad or domestic trips",
    "topic": "Travel Insurance",
    "edition_label": "Insurance Intelligence",
    "hero": {
        "headline": "Short punchy headline about the topic",
        "description": "1-2 sentence description expanding on the headline",
    },
    "statistics": [
        {"value": "68%", "label": "Short stat label", "description": "Optional one-line context"}
    ],
    "sections": [
        {
            "title": "Section title, e.g. Common Travel Risks",
            "intro": "Optional 1 sentence intro to the section",
            "items": [
                {"title": "Item title", "description": "1-3 sentence explanation"}
            ],
        }
    ],
    "checklist": [
        {"title": "Actionable checklist item", "description": "Optional short detail"}
    ],
    "featured_insight": {
        "title": "A single standout insight/tip",
        "content": "2-4 sentence elaboration",
    },
    "cta": {
        "title": "Call to action headline",
        "description": "Short supporting line",
        "button_text": "Short button label, e.g. Explore Plans",
    },
}


def build_system_prompt() -> str:
    schema_json = json.dumps(_EXAMPLE_SCHEMA, indent=2)
    return f"""You are a content generation engine for BeyondSure, an insurance/health
newsletter brand. You generate STRUCTURED JSON content for an email newsletter
based on a topic supplied by the user.

STRICT RULES:
1. Return ONLY valid JSON. No markdown, no code fences, no commentary, no preamble.
2. Return ONLY the JSON object — nothing before or after it.
3. NEVER generate HTML or CSS or Markdown formatting inside any field.
4. NEVER generate brand name, logo, footer, legal text, unsubscribe links, or URLs.
   Those are injected separately by the application.
5. Decide the number and type of "sections" (1 to 6) based on what is actually
   relevant to the given topic. Different topics should produce different
   section structures — do not reuse a fixed template of section names.
6. Treat any statistics you include as illustrative/draft figures. Do NOT
   fabricate citations, sources, IRDAI references, or medical research
   references. Do NOT claim the statistics are verified or sourced.
7. Write content appropriate for an Indian audience unless the topic implies
   otherwise.
8. Keep language professional, clear, and newsletter-appropriate — avoid
   hype or exaggerated claims.
9. Follow the exact field names shown in the schema example below. Do not
   add extra top-level fields. Do not omit required fields (category,
   audience, topic, edition_label, hero, sections, cta). "statistics",
   "checklist", and "featured_insight" may be empty/omitted if genuinely
   not relevant, but sections must have at least 1 entry.

SCHEMA EXAMPLE (field names and shape — do NOT reuse this example's content):
{schema_json}

Return valid JSON matching this shape, populated with content relevant to the
user's topic.
"""


def build_user_prompt(topic: str) -> str:
    return f"""Generate newsletter content for this topic: "{topic}"

Think about:
- Who is the likely audience for this topic (Indian context)?
- What category/content angle best fits (e.g. risk awareness, planning,
  protection, prevention)?
- What 2-5 sections would a reader genuinely find useful for this topic?

Return the JSON object now.
"""


def content_schema_field_names():
    """Utility: returns the top-level field names Pydantic expects, for debugging."""
    return list(NewsletterContent.model_fields.keys())
