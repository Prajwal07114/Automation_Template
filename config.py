"""
Fixed brand + app configuration.

Everything in BRAND is controlled by Python/Jinja2 ONLY.
The LLM never sees this and never generates any of it.
"""

import os

from dotenv import load_dotenv


load_dotenv()


# ============================================================
# GROQ CONFIGURATION
# ============================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to your .env file."
    )

GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "llama-3.3-70b-versatile"
)

MAX_LLM_RETRIES = int(
    os.getenv("MAX_LLM_RETRIES", "2")
)


# ============================================================
# FIXED BRAND CONFIGURATION
# ============================================================

BRAND = {
    "name": "BeyondSure",
    "logo_text": "BeyondSure",
    "tagline": "Insurance Intelligence, Simplified",

    "primary_color": "#0B3D91",
    "accent_color": "#00A99D",
    "text_color": "#1A1A1A",
    "muted_color": "#6B7280",
    "background_color": "#F4F6F8",
    "card_background": "#FFFFFF",

    "website_url": "https://www.beyondsure.in",

    "cta_base_url": "https://www.beyondsure.in/",

    "unsubscribe_url": "https://www.beyondsure.in/",

    "contact_email": "support@beyondsure.in",

    "social_links": {
        "LinkedIn": "https://www.linkedin.com/",
        "Twitter": "https://twitter.com/",
        "Instagram": "https://instagram.com/",
    },

    "legal_text": (
        "This email is intended for informational purposes only and does not "
        "constitute financial, medical, or insurance advice. Please consult a "
        "licensed advisor before making any decisions."
    ),

    "address": "BeyondSure Insurance Services, India",
}