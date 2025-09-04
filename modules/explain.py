from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Metrics:
    pe: float | None = None
    ev_ebitda: float | None = None
    roic: float | None = None  # not available from yfinance directly
    wacc: float | None = None  # placeholder
    fcf_yield: float | None = None  # placeholder
    debt_ebitda: float | None = None  # placeholder

def _fmt(x, suffix=""):
    if x is None: 
        return "ukendt"
    try:
        return f"{x:.2f}{suffix}"
    except Exception:
        return str(x)

def explain_metrics(m: Metrics, bente_mode: bool = True) -> List[str]:
    lines = []
    if m.pe is not None:
        if m.pe > 30:
            rel = "ret højt"
        elif m.pe < 12:
            rel = "ret lavt"
        else:
            rel = "omkring middel"
        if bente_mode:
            lines.append(f"P/E {_fmt(m.pe)}: det er {rel}. Det betyder cirka hvad du betaler for \n"
                         "årets overskud pr. aktie. Højt tal = store forventninger.")
        else:
            lines.append(f"P/E {_fmt(m.pe)} ({rel}). Pris pr. årlig indtjening pr. aktie.")
    if m.ev_ebitda is not None:
        if bente_mode:
            lines.append(f"EV/EBITDA {_fmt(m.ev_ebitda)}: cirka prisskiltet for hele virksomheden i forhold til "
                         "årets driftsindtjening. Bruges til at sammenligne på tværs af gældsniveauer.")
        else:
            lines.append(f"EV/EBITDA {_fmt(m.ev_ebitda)}: enterprise value i forhold til driftsindtjening.")
    if m.fcf_yield is not None:
        if bente_mode:
            lines.append(f"FCF‑yield {_fmt(m.fcf_yield, '%')}: kontant afkast til ejerne i procent af aktiekursen. "
                         "Højt kan være attraktivt, men tjek risiko.")
        else:
            lines.append(f"FCF‑yield {_fmt(m.fcf_yield, '%')}.")
    if m.debt_ebitda is not None:
        if bente_mode:
            lines.append(f"Gæld/EBITDA {_fmt(m.debt_ebitda, 'x')}: så mange år at afdrage gælden ved uændret indtjening.")
        else:
            lines.append(f"Netto gæld / EBITDA {_fmt(m.debt_ebitda, 'x')}.")
    if not lines:
        lines.append("Ingen nøgletal tilgængelige lige nu.")
    return lines

def explain_move(stock_ret: float, market_ret: float, sector_ret: float | None, 
                 volume_ratio: float | None, news_flags: Dict[str,bool]) -> List[str]:
    reasons = []
    # Market/sector drift
    if abs(stock_ret - market_ret) < 0.4:
        reasons.append("Det ligner en bred markedsbevægelse i dag.")
    if sector_ret is not None and abs(stock_ret - sector_ret) < 0.4:
        reasons.append("Aktien fulgte sektorens retning.")
    # Events
    if news_flags.get('earnings'): reasons.append("Regnskab/guidance nævnes i nyhederne.")
    if news_flags.get('downgrade'): reasons.append("Analytiker sænkede anbefaling/kursmål.")
    if news_flags.get('upgrade'): reasons.append("Analytiker hævede anbefaling/kursmål.")
    if news_flags.get('mna'): reasons.append("M&A‑rygter eller aftaler kan have påvirket kursen.")
    if volume_ratio is not None and volume_ratio > 2:
        reasons.append("Usædvanligt høj handel – tyder på nyheds- eller floweffekt.")
    if not reasons:
        reasons.append("Ingen klar enkeltårsag – sandsynligvis generel stemning og nyhedsflow.")
    return reasons
