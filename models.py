"""
Pydantic models for the structured newsletter content.

This is the CONTRACT between the LLM and the rest of the app.
The LLM must return JSON that validates against `NewsletterContent`.
If it doesn't, generator.py will retry / raise an error — it will
NEVER be silently patched into something that "looks right".
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class Hero(BaseModel):
    headline: str = Field(..., min_length=3, max_length=140)
    description: str = Field(..., min_length=10, max_length=400)


class Statistic(BaseModel):
    value: str = Field(..., min_length=1, max_length=20)
    label: str = Field(..., min_length=1, max_length=80)
    description: Optional[str] = Field(default=None, max_length=200)


class SectionItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=500)


class Section(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    intro: Optional[str] = Field(default=None, max_length=300)
    items: List[SectionItem] = Field(default_factory=list, min_length=1, max_length=8)


class ChecklistItem(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=250)


class FeaturedInsight(BaseModel):
    title: str = Field(..., min_length=1, max_length=140)
    content: str = Field(..., min_length=10, max_length=600)


class CTA(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    description: str = Field(..., min_length=1, max_length=300)
    button_text: str = Field(..., min_length=1, max_length=40)


class NewsletterContent(BaseModel):
    """
    Full structured output the LLM must produce.
    Everything here is TOPIC-SPECIFIC content only.
    Brand/footer/legal/URLs are NEVER part of this model —
    those live in config.py and are injected at render time.
    """

    category: str = Field(..., min_length=2, max_length=80)
    audience: str = Field(..., min_length=2, max_length=120)
    topic: str = Field(..., min_length=2, max_length=120)
    edition_label: str = Field(..., min_length=2, max_length=80)

    hero: Hero
    statistics: List[Statistic] = Field(default_factory=list, max_length=6)
    sections: List[Section] = Field(..., min_length=1, max_length=8)
    checklist: List[ChecklistItem] = Field(default_factory=list, max_length=8)
    featured_insight: Optional[FeaturedInsight] = None
    cta: CTA


class GenerateEmailRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=120, description="Any topic, e.g. 'Cyber Insurance'")


class GenerateEmailResponse(BaseModel):
    topic: str
    category: str
    content: NewsletterContent
    html: str
