# Campus Draft V2

A Streamlit drafting game with 60+ universities, 36 majors, degree-specific scoring, richer outcomes, and optional AI career stories.

## Files

- `app.py` — interface and session flow
- `game_logic.py` — scoring, outcomes, identities, and fallback stories
- `story_generator.py` — optional OpenAI story generation
- `data/universities.json` — university game data
- `data/majors.json` — major data
- `data/synergies.json` — cross-major bonuses

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Optional AI stories

Create `.streamlit/secrets.toml` locally:

```toml
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-4.1-mini"
```

Never commit the real secrets file. The included `.gitignore` blocks it.

On Streamlit Community Cloud, open the app settings, choose **Secrets**, and paste the same two lines there.

Without an API key, the game still works and uses a built-in deterministic story generator.
