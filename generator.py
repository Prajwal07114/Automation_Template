"""
LLM integration layer.

Responsible ONLY for:
- calling the Groq API
- extracting JSON from the response
- validating the response against NewsletterContent

Provider-specific code lives here so the provider can be swapped later
without changing app.py.
"""

import json
import re

from groq import Groq
from pydantic import ValidationError

from config import GROQ_API_KEY, GROQ_MODEL, MAX_LLM_RETRIES
from models import NewsletterContent
from prompts import build_system_prompt, build_user_prompt


client = Groq(api_key=GROQ_API_KEY)


class GenerationError(Exception):
    """Raised when the LLM fails to produce valid content after retries."""


def _extract_json(raw_text: str) -> dict:
    """
    Extract a JSON object from the model response.
    Handles normal JSON and JSON inside markdown code fences.
    """

    text = raw_text.strip()

    # Handle ```json ... ``` responses
    fence_match = re.search(
        r"```(?:json)?\s*(\{.*\})\s*```",
        text,
        re.DOTALL,
    )

    if fence_match:
        text = fence_match.group(1)

    # Fallback: find first JSON object
    if not text.startswith("{"):
        brace_match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL,
        )

        if brace_match:
            text = brace_match.group(0)

    return json.loads(text)


def _call_llm(topic: str) -> str:
    """
    Call Groq and return the generated text.
    """

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=2000,
        messages=[
            {
                "role": "system",
                "content": build_system_prompt(),
            },
            {
                "role": "user",
                "content": build_user_prompt(topic),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("Groq returned an empty response.")

    return content


def generate_newsletter_content(topic: str) -> NewsletterContent:
    """
    Calls Groq, parses JSON, validates it using Pydantic,
    and retries if the generated content is invalid.
    """

    last_error: Exception | None = None

    for attempt in range(1, MAX_LLM_RETRIES + 2):
        try:
            raw_text = _call_llm(topic)

            parsed = _extract_json(raw_text)

            content = NewsletterContent.model_validate(parsed)

            return content

        except json.JSONDecodeError as e:
            last_error = e

        except ValidationError as e:
            last_error = e

        except Exception as e:
            last_error = e

    raise GenerationError(
        f"Failed to generate valid newsletter content for topic "
        f"'{topic}' after {MAX_LLM_RETRIES + 1} attempt(s). "
        f"Last error: {last_error}"
    )