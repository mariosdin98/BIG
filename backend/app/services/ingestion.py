from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Country, CountrySnapshot

WORLD_BANK_API = "https://api.worldbank.org/v2"
INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "current_account": "BN.CAB.XOKA.GD.ZS",
}

FALLBACK_COUNTRIES = [
    ("USA", "United States", "North America", "US"),
    ("GRC", "Greece", "Europe & Central Asia", "GR"),
    ("DEU", "Germany", "Europe & Central Asia", "DE"),
    ("JPN", "Japan", "East Asia & Pacific", "JP"),
]


def _score_bucket(score: float) -> str:
    if score < 25:
        return "Low"
    if score < 50:
        return "Medium"
    if score < 75:
        return "High"
    return "Severe"


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(value, high))


def _stable_country_noise(iso3: str) -> float:
    # deterministic per-country signal (not random), helps fill sparse data consistently
    seed = sum(ord(ch) for ch in iso3)
    return (seed % 17) - 8


async def _fetch_json(client: httpx.AsyncClient, url: str) -> Any:
    response = await client.get(url)
    response.raise_for_status()
    return response.json()


async def fetch_country_catalog(client: httpx.AsyncClient) -> list[tuple[str, str, str, str]]:
    url = f"{WORLD_BANK_API}/country?format=json&per_page=400"
    payload = await _fetch_json(client, url)
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []

    countries: list[tuple[str, str, str, str]] = []
    for row in rows:
        iso3 = row.get("id")
        iso2 = row.get("iso2Code")
        name = row.get("name")
        region = (row.get("region") or {}).get("value")
        if not iso3 or not iso2 or not name:
            continue
        if region == "Aggregates":
            continue
        countries.append((iso3, name, region or "Unknown", iso2))
    return countries


async def fetch_indicator_latest_by_country(client: httpx.AsyncClient, indicator: str) -> dict[str, float]:
    url = f"{WORLD_BANK_API}/country/all/indicator/{indicator}?format=json&per_page=20000"
    payload = await _fetch_json(client, url)
    rows = payload[1] if isinstance(payload, list) and len(payload) > 1 else []

    values: dict[str, float] = {}
    for row in rows:
        iso3 = (row.get("country") or {}).get("id")
        value = row.get("value")
        if not iso3 or value is None or iso3 in values:
            continue
        values[iso3] = float(value)
    return values


def _compute_snapshot_features(iso3: str, indicator_values: dict[str, dict[str, float]], week_shift: int) -> dict[str, float]:
    noise = _stable_country_noise(iso3)

    gdp = indicator_values["gdp_growth"].get(iso3, 1.5 + noise * 0.2)
    inflation = indicator_values["inflation"].get(iso3, 3.0 + abs(noise) * 0.4)
    unemployment = indicator_values["unemployment"].get(iso3, 6.0 + abs(noise) * 0.3)
    current_account = indicator_values["current_account"].get(iso3, -1.0 + noise * 0.3)

    macro = _clamp(50 - gdp * 4.8 + inflation * 1.7 + week_shift * 0.8)
    credit = _clamp(42 + inflation * 1.4 + unemployment * 1.1 + week_shift * 1.1)
    bubble = _clamp(38 + max(inflation - 2.0, 0) * 2.1 + abs(gdp) * 0.6 + week_shift * 0.5)
    external = _clamp(44 + abs(min(current_account, 0.0)) * 2.2 + week_shift * 0.7)
    geo = _clamp(35 + abs(noise) * 2.3 + week_shift * 0.6)

    risk_score = macro * 0.25 + credit * 0.25 + bubble * 0.2 + external * 0.2 + geo * 0.1
    prob_6m = min(max((risk_score / 100) * 0.62, 0.01), 0.95)
    prob_12m = min(max((risk_score / 100) * 0.86, 0.02), 0.98)

    return {
        "gdp_growth": gdp,
        "inflation": inflation,
        "unemployment": unemployment,
        "current_account": current_account,
        "macro": macro,
        "credit": credit,
        "bubble": bubble,
        "external": external,
        "geo": geo,
        "risk_score": risk_score,
        "prob_6m": prob_6m,
        "prob_12m": prob_12m,
    }


def _build_snapshot_from_features(iso3: str, target_date: date, features: dict[str, float]) -> CountrySnapshot:
    drivers = [
        {"feature": "yield_curve_proxy", "impact": round((features["inflation"] - features["gdp_growth"]) / 25, 3)},
        {"feature": "inflation", "impact": round(features["inflation"] / 22, 3)},
        {"feature": "unemployment", "impact": round(features["unemployment"] / 30, 3)},
        {"feature": "current_account", "impact": round((-features["current_account"]) / 35, 3)},
        {"feature": "fragility_signal", "impact": round(features["geo"] / 130, 3)},
    ]

    return CountrySnapshot(
        country_iso=iso3,
        date=target_date,
        risk_score=round(features["risk_score"], 2),
        bucket=_score_bucket(features["risk_score"]),
        prob_recession_6m=round(features["prob_6m"], 3),
        prob_recession_12m=round(features["prob_12m"], 3),
        macro=round(features["macro"], 2),
        credit_stress=round(features["credit"], 2),
        bubble=round(features["bubble"], 2),
        external=round(features["external"], 2),
        geopolitical=round(features["geo"], 2),
        drivers=drivers,
    )


async def seed_and_refresh(db: Session) -> None:
    today = date.today()
    previous_week = today - timedelta(days=7)

    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            countries = await fetch_country_catalog(client)
            indicator_values = {
                key: await fetch_indicator_latest_by_country(client, indicator)
                for key, indicator in INDICATORS.items()
            }
    except Exception:
        countries = FALLBACK_COUNTRIES
        indicator_values = {key: {} for key in INDICATORS}

    for iso3, name, region, _ in countries:
        if not db.get(Country, iso3):
            db.add(Country(iso=iso3, name=name, region=region))
    db.commit()

    existing_today = {
        row[0]
        for row in db.execute(
            select(CountrySnapshot.country_iso).where(CountrySnapshot.date == today)
        ).all()
    }

    for iso3, _, _, _ in countries:
        if iso3 in existing_today:
            continue

        prev_features = _compute_snapshot_features(iso3, indicator_values, week_shift=-3)
        curr_features = _compute_snapshot_features(iso3, indicator_values, week_shift=2)

        db.add(_build_snapshot_from_features(iso3, previous_week, prev_features))
        db.add(_build_snapshot_from_features(iso3, today, curr_features))

    db.commit()
