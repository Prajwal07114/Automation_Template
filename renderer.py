"""
Renders validated NewsletterContent + fixed BRAND config into final HTML
using the single generic Jinja2 template.
"""

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import BRAND
from models import NewsletterContent

TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
)


def render_newsletter_html(content: NewsletterContent) -> str:
    template = _env.get_template("newsletter.html")
    return template.render(
        brand=BRAND,
        content=content,
        today=date.today().strftime("%B %d, %Y"),
    )
