# Campus Draft

A simple Streamlit game inspired by the rapid draft-and-result loop of roster-building games.

## Gameplay

- Three rounds: Undergraduate, Master's, and PhD
- Each round reveals a random major and three universities
- Draft one university for each credential
- Use one major reroll and one university reroll per game
- Receive a fictional career outcome, net-worth tier, and campus identity

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py`, `requirements.txt`, and this README.
3. In Streamlit Community Cloud, choose **Deploy a public app from GitHub**.
4. Select the repository and set the main file path to `app.py`.
5. Deploy.

## Notes

The ratings and outcomes are fictional game-design estimates. The app uses university names as plain text and does not use official logos or branding.
