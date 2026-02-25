from __future__ import annotations

from datetime import date, timedelta

from app.core.schemas import Alert, CountryLatest, HeatmapPoint, Subindices

COUNTRIES = {
    "USA": {"name": "United States", "region": "North America"},
    "GRC": {"name": "Greece", "region": "Europe"},
    "DEU": {"name": "Germany", "region": "Europe"},
    "JPN": {"name": "Japan", "region": "Asia"},
    "BRA": {"name": "Brazil", "region": "South America"},
}

COUNTRY_HISTORY: dict[str, list[CountryLatest]] = {}
ALERTS: list[Alert] = []
ALERT_RULES: list[dict] = []
PORTFOLIOS: dict[str, dict] = {}


def risk_bucket(score: float) -> str:
    if score >= 80:
        return "Severe"
    if score >= 65:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def seed_data() -> None:
    if COUNTRY_HISTORY:
        return

    today = date.today()
    template = {
        "USA": (54, 62, 51, 46, 43),
        "GRC": (60, 71, 58, 65, 56),
        "DEU": (49, 55, 44, 42, 35),
        "JPN": (52, 57, 48, 47, 39),
        "BRA": (63, 69, 62, 68, 61),
    }

    for iso, (macro, credit, bubble, external, geo) in template.items():
        rows: list[CountryLatest] = []
        for i in range(24):
            dt = today - timedelta(days=(23 - i) * 30)
            shift = (i - 12) * 0.6
            subindices = Subindices(
                macro=max(0, min(100, macro + shift * 0.7)),
                credit_stress=max(0, min(100, credit + shift * 1.1)),
                bubble=max(0, min(100, bubble + shift * 0.5)),
                external=max(0, min(100, external + shift * 0.9)),
                geopolitical=max(0, min(100, geo + shift * 0.6)),
            )
            score = (
                subindices.macro * 0.25
                + subindices.credit_stress * 0.25
                + subindices.bubble * 0.2
                + subindices.external * 0.2
                + subindices.geopolitical * 0.1
            )
            latest = CountryLatest(
                country=iso,
                date=dt,
                risk_score=round(score, 1),
                bucket=risk_bucket(score),
                prob_recession_6m=round(min(0.95, max(0.05, (score - 30) / 100)), 2),
                prob_recession_12m=round(min(0.98, max(0.1, (score - 20) / 100)), 2),
                subindices=subindices,
                drivers=[
                    {"feature": "yield_curve_slope", "impact": round(subindices.credit_stress / 800, 3)},
                    {"feature": "fx_3m_drawdown", "impact": round(subindices.external / 900, 3)},
                    {"feature": "pmi_delta", "impact": round(subindices.macro / 950, 3)},
                    {"feature": "credit_to_gdp_gap", "impact": round(subindices.bubble / 1000, 3)},
                    {"feature": "geopolitical_incidents", "impact": round(subindices.geopolitical / 1200, 3)},
                ],
            )
            rows.append(latest)
        COUNTRY_HISTORY[iso] = rows

    ALERTS.extend(
        [
            Alert(
                id="a1",
                country="BRA",
                date=today,
                severity="warning",
                message="Country: BRA | Risk +11 (week) | Drivers: yield vol, FX drawdown, PMI drop",
            ),
            Alert(
                id="a2",
                country="GRC",
                date=today - timedelta(days=1),
                severity="critical",
                message="Country: GRC | Regime shift Elevated -> Crisis in credit stress",
            ),
        ]
    )


def latest_heatmap() -> list[HeatmapPoint]:
    points: list[HeatmapPoint] = []
    for iso, hist in COUNTRY_HISTORY.items():
        latest = hist[-1]
        previous = hist[-2]
        points.append(
            HeatmapPoint(
                iso=iso,
                name=COUNTRIES[iso]["name"],
                risk_score=latest.risk_score,
                bucket=latest.bucket,
                wow_change=round(latest.risk_score - previous.risk_score, 1),
            )
        )
    return sorted(points, key=lambda x: x.risk_score, reverse=True)
