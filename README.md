# AI Aktiehjælper – Bente-mode (v2)

En Streamlit-app der:

- Viser interaktiv kursgraf (candlestick + volumen)
- Har to tydelige knapper: **Analyser nøgletal** og **Forklaring på kurs**
- Forklarer nøgletal i *Bente-mode* (ingen jargon)
- Sammenligner nøgletal med **sektor** og valgfrit **peers**-input
- Giver sandsynlig forklaring på kursbevægelse med nyhedskilder
- Tidsvælger: 1D, 1U, 1M, 1Å, 5Å, Max

## Kør lokalt
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
