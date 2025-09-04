from dataclasses import dataclass
from typing import Optional, List, Dict

@dataclass
class Metrics:
    pe: Optional[float] = None
    fpe: Optional[float] = None
    ps: Optional[float] = None
    pb: Optional[float] = None
    ev_ebitda: Optional[float] = None
    gross_margin: Optional[float] = None
    op_margin: Optional[float] = None
    net_margin: Optional[float] = None
    roa: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    debt_ebitda: Optional[float] = None
    fcf_yield: Optional[float] = None  # placeholder

def _fmt(x, suffix=""):
    if x is None:
        return "ukendt"
    try:
        return f"{x:.2f}{suffix}"
    except Exception:
        return str(x)

def _band(val, low, high):
    if val is None: return "ukendt niveau"
    if val < low: return "lavt"
    if val > high: return "højt"
    return "omkring normalt"

def explain_metrics(m: Metrics, hist_context: Dict[str,float], sector_hint: str|None) -> List[str]:
    lines = []
    # Pris ift indtjening
    if m.pe is not None or m.fpe is not None:
        parts = []
        if m.pe is not None:
            parts.append(f"P/E {_fmt(m.pe)}")
        if m.fpe is not None:
            parts.append(f"Fwd P/E {_fmt(m.fpe)}")
        base = " og ".join(parts)
        tail = []
        if 'pe_pct5y' in hist_context:
            tail.append(f"ca. {int(hist_context['pe_pct5y'])}%-percentil i egen 5-års historik")
        if sector_hint:
            tail.append(f"sektor: {sector_hint}")
        extra = f"; {', '.join(tail)}" if tail else ""
        lines.append(f"{base}: fortæller hvad du betaler i pris for én krones (forventede) årsoverskud. Højere tal betyder, at markedet forventer mere vækst{extra}.")
    # EV/EBITDA
    if m.ev_ebitda is not None:
        lines.append(f"EV/EBITDA {_fmt(m.ev_ebitda)} ({_band(m.ev_ebitda,7,18)}): omtrent prisskiltet for hele virksomheden i forhold til årets driftsindtjening. Godt til at sammenligne firmaer med forskellig gæld.")
    # P/S og P/B
    if m.ps is not None:
        lines.append(f"P/S {_fmt(m.ps)}: pris i forhold til omsætning. Bruges især til vækstvirksomheder hvor profit svinger.")
    if m.pb is not None:
        lines.append(f"P/B {_fmt(m.pb)}: pris i forhold til bogført egenkapital. Lavt kan være 'billigt' – eller et tegn på problemer; kræver kontekst.")
    # Marginer
    if m.gross_margin is not None:
        lines.append(f"Brutto-margin {_fmt(100*m.gross_margin,'%')}: hvor meget der er tilbage efter at have produceret varen.")
    if m.op_margin is not None:
        lines.append(f"EBIT-margin {_fmt(100*m.op_margin,'%')}: hvor meget driften tjener før renter og skat.")
    if m.net_margin is not None:
        lines.append(f"Netto-margin {_fmt(100*m.net_margin,'%')}: hvor meget ender som bundlinje til sidst.")
    # Afkast
    if m.roa is not None:
        lines.append(f"ROA {_fmt(100*m.roa,'%')}: hvor effektivt virksomheden bruger sine aktiver.")
    if m.roe is not None:
        lines.append(f"ROE {_fmt(100*m.roe,'%')}: 'renten' ejerne får på deres penge. Høj og stabil ROE er ofte et kvalitetstegn.")
    # Gæld
    if m.debt_to_equity is not None:
        lines.append(f"Gæld/Egenkapital {_fmt(m.debt_to_equity)}: hvor stor gælden er i forhold til egenkapitalen. Høj værdi = mere følsom for rentestigninger.")
    if m.debt_ebitda is not None:
        lines.append(f"Gæld/EBITDA {_fmt(m.debt_ebitda,'x')}: omtrent hvor mange år det tager at afdrage gælden, hvis indtjeningen står stille.")
    if m.fcf_yield is not None:
        lines.append(f"FCF-yield {_fmt(100*m.fcf_yield,'%')}: kontant afkast til ejerne i procent af kursen (indikator, ikke garanti)." )
    if not lines:
        lines.append("Ingen nøgletal tilgængelige.")
    return lines

def human_explain_price_move(period_label: str, ret_pct: float, market_ret: float|None,
                             sector_ret: float|None, volume_ratio: float|None,
                             news_flags: Dict[str,bool]) -> List[str]:
    out = []
    out.append(f"Udvikling {period_label}: {ret_pct:+.2f}%.")
    if market_ret is not None:
        out.append(f"Marked: {market_ret:+.2f}%.")
    if sector_ret is not None:
        out.append(f"Sektor: {sector_ret:+.2f}%.")
    reasons = []
    if market_ret is not None and abs(ret_pct - market_ret) < 0.5:
        reasons.append("bevægelsen ligner bredt marked")
    if sector_ret is not None and abs(ret_pct - sector_ret) < 0.5:
        reasons.append("aktien fulgte sektoren")
    if volume_ratio and volume_ratio > 1.8:
        reasons.append("usædvanlig høj handel tyder på nyheds-/floweffekt")
    if news_flags.get('earnings'): reasons.append("regnskab/guidance i nyhederne")
    if news_flags.get('upgrade'): reasons.append("analytiker-opjustering")
    if news_flags.get('downgrade'): reasons.append("analytiker-nedjustering")
    if news_flags.get('mna'): reasons.append("M&A-rygter/aftaler")
    if not reasons:
        reasons.append("ingen enkeltårsag – sandsynligvis generel stemning og nyhedsmix")
    out.append("Sandsynlige forklaringer: " + "; ".join(reasons) + ".")
    return out
