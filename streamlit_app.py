"""
BeyondSure Email Generator — Streamlit demo frontend.

This is a thin UI layer only. It does NOT generate content itself —
it calls the existing FastAPI backend (POST /generate-email), which
handles: Grok/xAI LLM -> structured JSON -> Pydantic validation ->
Jinja2 -> HTML email. This file just sends the topic and displays
whatever HTML comes back.
"""

import requests
import streamlit as st

BACKEND_URL = "http://127.0.0.1:8001/generate-email"

st.set_page_config(page_title="BeyondSure Email Generator", layout="wide")

st.title("BeyondSure Email Generator")
st.write("Enter any topic and generate a BeyondSure-style HTML newsletter.")

topic = st.text_input(
    "Enter Topic",
    placeholder="e.g. Senior Health, Motor Insurance, Cyber Insurance",
)

generate_clicked = st.button("Generate Email")

if generate_clicked:
    if not topic.strip():
        st.error("Please enter a topic.")
    else:
        with st.spinner("Generating newsletter..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"topic": topic.strip()},
                    timeout=60,
                )
            except requests.exceptions.RequestException:
                st.error("Could not connect to the email generator backend.")
                response = None

        if response is not None:
            if response.status_code != 200:
                st.error(
                    f"Backend returned an error (status {response.status_code}): "
                    f"{response.text}"
                )
            else:
                # The backend returns JSON with an "html" field
                # (see GenerateEmailResponse in models.py). Fall back to
                # treating the body as raw HTML if that ever changes.
                content_type = response.headers.get("content-type", "")
                html = None

                if "application/json" in content_type:
                    data = response.json()
                    html = data.get("html")
                    if html is None:
                        st.error(
                            "Backend response did not contain an 'html' field. "
                            "Raw response shown below for debugging."
                        )
                        st.json(data)
                else:
                    # Backend returned raw HTML directly (e.g. the
                    # /generate-email/preview style endpoint).
                    html = response.text

                if html:
                    st.success("Email generated successfully.")

                    st.download_button(
                        label="Download HTML",
                        data=html,
                        file_name=f"{topic.strip().replace(' ', '_').lower()}_newsletter.html",
                        mime="text/html",
                    )

                    st.subheader("Preview")
                    st.components.v1.html(html, height=800, scrolling=True)
