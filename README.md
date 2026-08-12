# BeyondSure Dynamic Email Template Generator (MVP)

An internship MVP that accepts **any topic** and produces a branded, structured
HTML newsletter email — without hand-writing a template per topic.

```
ANY TOPIC → LLM (JSON only) → Pydantic validation → Jinja2 (1 generic template) → HTML EMAIL
```

## Why this architecture

- **The LLM never writes HTML.** It only returns structured JSON describing
  the content (hero, statistics, sections, checklist, CTA, etc). This keeps
  brand styling, legal/footer text, and layout 100% controlled by code —
  never hallucinated by the model.
- **Pydantic (`models.py`)** is the hard contract the LLM output must satisfy.
  Invalid/malformed JSON is rejected and retried, never silently patched.
- **One Jinja2 template (`templates/newsletter.html`)** renders every topic.
  It loops over `sections`, `statistics`, and `checklist` — it has no idea
  what topic it's rendering. Adding a new topic requires **zero** template
  changes.
- **Fixed brand data (`config.py`)** — brand name, logo, footer, social
  links, unsubscribe URL, legal text — is injected at render time and is
  never part of the LLM's job.

## ⚠️ Important note on factual content

This MVP does **not** implement RAG, web search, or any fact-verification.
Any statistics or factual claims the LLM generates are **draft/unverified**
content. The system explicitly instructs the LLM not to fabricate sources,
citations, IRDAI references, or medical research references, and not to
claim any figure is verified — but a human should always **review generated
content before it is actually sent as an email**.

## Project structure

```
beyondsure-email-generator/
├── app.py              # FastAPI app: /health, /generate-email
├── models.py            # Pydantic schema for LLM output + API request/response
├── generator.py          # Anthropic API call, JSON extraction, retry logic
├── prompts.py            # System + user prompt construction
├── renderer.py            # Jinja2 rendering
├── config.py              # Fixed brand data (LLM never touches this)
├── templates/
│   └── newsletter.html      # THE single generic email template
├── requirements.txt
├── .env.example
└── README.md
```

## Setup (Windows)

1. **Install Python 3.11+** if you haven't already (python.org, check "Add to PATH").

2. **Open PowerShell / Command Prompt in the project folder:**
   ```
   cd beyondsure-email-generator
   ```

3. **Create and activate a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Set up your API key:**
   ```
   copy .env.example .env
   ```
   Then open `.env` in a text editor and paste your real Anthropic API key:
   ```
   ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
   ```

## Setup (macOS / Linux)

```bash
cd beyondsure-email-generator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your ANTHROPIC_API_KEY
```

## Running the server

```
uvicorn app:app --reload
```

The API will be live at: `http://127.0.0.1:8000`

## Testing via Swagger UI

1. Go to: `http://127.0.0.1:8000/docs`
2. Expand `POST /generate-email`
3. Click **Try it out**
4. Enter a request body:
   ```json
   { "topic": "Cyber Insurance" }
   ```
5. Click **Execute** — the response will contain the structured `content`
   JSON and the rendered `html` string.

There's also `POST /generate-email/preview`, which returns raw HTML directly
(open it in a browser tab, or use curl and redirect to a `.html` file) so you
can visually check the rendered email without picking apart JSON.

## Example requests

**Health check:**
```bash
curl http://127.0.0.1:8000/health
```
```json
{ "status": "healthy" }
```

**Generate an email:**
```bash
curl -X POST http://127.0.0.1:8000/generate-email ^
  -H "Content-Type: application/json" ^
  -d "{\"topic\": \"Travel Insurance\"}"
```
(On macOS/Linux, use single quotes instead of `^` line continuations.)

**Save rendered HTML directly to a file for viewing:**
```bash
curl -X POST http://127.0.0.1:8000/generate-email/preview \
  -H "Content-Type: application/json" \
  -d '{"topic": "Diabetes Management"}' \
  -o preview.html
```
Then open `preview.html` in any browser.

### Example JSON response shape

```json
{
  "topic": "Travel Insurance",
  "category": "Travel Insurance",
  "content": {
    "category": "Travel Insurance",
    "audience": "Indian travelers going abroad or on domestic trips",
    "topic": "Travel Insurance",
    "edition_label": "Insurance Intelligence",
    "hero": {
      "headline": "Don't Let a Trip Mishap Become a Financial Setback",
      "description": "From missed flights to medical emergencies abroad, ..."
    },
    "statistics": [
      { "value": "1 in 5", "label": "Trips face a disruption", "description": "Illustrative estimate" }
    ],
    "sections": [
      {
        "title": "Common Travel Risks",
        "intro": "Understanding what can go wrong helps you plan ahead.",
        "items": [
          { "title": "Flight Delays & Cancellations", "description": "..." }
        ]
      }
    ],
    "checklist": [
      { "title": "Check policy exclusions before departure", "description": "..." }
    ],
    "featured_insight": {
      "title": "Pre-existing Conditions Aren't Always Covered",
      "content": "..."
    },
    "cta": {
      "title": "Compare Travel Insurance Plans",
      "description": "Find coverage that matches your itinerary.",
      "button_text": "Explore Plans"
    }
  },
  "html": "<!DOCTYPE html>..."
}
```

## Topics to test (all use the SAME template/pipeline)

- Senior Health
- Motor Insurance
- Travel Insurance
- Diabetes Management
- Cyber Insurance
- Women's Health
- Employee Health Benefits
- Retirement Planning
- Monsoon Health

No new HTML file, template, or schema is needed for any of these — only the
`topic` string in the request changes.

## Known MVP limitations (by design)

- No database — nothing is persisted between requests.
- No authentication.
- No email-sending integration (this generates HTML only; sending is a
  separate concern for later).
- No RAG/web search — factual claims are LLM-generated and unverified.
- Retry logic is intentionally simple (a couple of attempts on invalid
  JSON/schema failures), not a production-grade resilience system.
