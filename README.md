# AI Stock Helper (MVP)

A tiny Streamlit app that explains stock metrics in plain Danish ("Bente‑mode") and
gives a likely reason for today's price move with news links.

## Run locally
1) Install Python 3.10+
2) Create a virtual environment and activate it (Windows PowerShell example):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```
macOS/Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
3) Install dependencies:
```
pip install -r requirements.txt
```
4) Launch:
```
streamlit run app.py
```
The app opens at http://localhost:8501

## Deploy (free & easy)
- **Streamlit Community Cloud**: push this folder to a public GitHub repo and create a new Streamlit app.
- **Hugging Face Spaces**: create a Space (Streamlit), upload these files, set `app_file=app.py`.

## Notes
- Data source is Yahoo Finance via `yfinance`. For production, consider paid APIs (Polygon, IEX, Finnhub) for reliability.
- This is **not investment advice**. Always verify and consider your risk tolerance.
