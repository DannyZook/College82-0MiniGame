from __future__ import annotations

import json
from typing import Any

import streamlit as st

from game_logic import fallback_story


def ai_available() -> bool:
    try:
        return bool(st.secrets.get("OPENAI_API_KEY"))
    except Exception:
        return False


def generate_story(roster: list[dict[str, Any]], result: dict[str, Any], identity: str) -> tuple[str, bool]:
    """Return (story, used_ai). Falls back cleanly when no key or request failure."""
    if not ai_available():
        return fallback_story(roster, result, identity), False

    try:
        from openai import OpenAI

        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        model = st.secrets.get("OPENAI_MODEL", "gpt-4.1-mini")
        payload = {
            "education": [
                {
                    "degree": item["degree"],
                    "major": item["major"],
                    "university": item["university"],
                    "credential_score": item["score"]["total"],
                }
                for item in roster
            ],
            "career_outcome": result["career_title"],
            "estimated_net_worth": result["wealth"],
            "industry": result["industry"],
            "career_style": result["career_style"],
            "campus_identity": identity,
            "required_twist": result["twist"],
        }
        response = client.responses.create(
            model=model,
            instructions=(
                "Write a fictional, entertaining, believable career story for a college drafting game. "
                "Use 120-180 words in 2 short paragraphs. Follow every supplied outcome exactly. "
                "Do not change the career tier, net-worth range, universities, majors, or campus identity. "
                "Connect all three degrees into one plausible career. Be specific and lightly humorous, not absurd. "
                "Do not claim this is a real prediction and do not mention scoring mechanics."
            ),
            input=json.dumps(payload, ensure_ascii=False),
        )
        story = response.output_text.strip()
        if not story:
            raise ValueError("The AI returned an empty story.")
        return story, True
    except Exception:
        return fallback_story(roster, result, identity), False
