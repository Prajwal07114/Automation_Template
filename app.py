"""
FastAPI application entrypoint.

Routes:
  GET  /health          -> liveness check
  POST /generate-email  -> { "topic": "..." } -> structured content + rendered HTML
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from models import GenerateEmailRequest, GenerateEmailResponse
from generator import generate_newsletter_content, GenerationError
from renderer import render_newsletter_html

app = FastAPI(
    title="BeyondSure Dynamic Email Template Generator",
    description=(
        "MVP: accepts any topic, uses an LLM to generate structured JSON "
        "content, validates it with Pydantic, and renders it into a "
        "branded HTML newsletter via a single generic Jinja2 template."
    ),
    version="0.1.0",
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/generate-email", response_model=GenerateEmailResponse)
def generate_email(request: GenerateEmailRequest):
    try:
        content = generate_newsletter_content(request.topic)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))

    html = render_newsletter_html(content)

    return GenerateEmailResponse(
        topic=request.topic,
        category=content.category,
        content=content,
        html=html,
    )


@app.post("/generate-email/preview", response_class=HTMLResponse)
def generate_email_preview(request: GenerateEmailRequest):
    """
    Convenience endpoint: returns raw HTML directly (renders in the browser)
    instead of JSON, for quick visual checks via Swagger/browser.
    """
    try:
        content = generate_newsletter_content(request.topic)
    except GenerationError as e:
        raise HTTPException(status_code=502, detail=str(e))

    return render_newsletter_html(content)
