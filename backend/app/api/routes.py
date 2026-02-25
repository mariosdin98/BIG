from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.core.schemas import AlertRuleIn, CountryMeta, PortfolioIn, PortfolioRisk
from app.services.store import (
    ALERTS,
    ALERT_RULES,
    COUNTRIES,
    COUNTRY_HISTORY,
    PORTFOLIOS,
    latest_heatmap,
    seed_data,
)

router = APIRouter()


@router.get("/countries", response_model=list[CountryMeta])
def get_countries() -> list[CountryMeta]:
    seed_data()
    return [CountryMeta(iso=iso, **meta) for iso, meta in COUNTRIES.items()]


@router.get("/countries/{iso}/latest")
def country_latest(iso: str):
    seed_data()
    hist = COUNTRY_HISTORY.get(iso.upper())
    if not hist:
        raise HTTPException(status_code=404, detail="Country not found")
    return hist[-1]


@router.get("/countries/{iso}/history")
def country_history(iso: str, from_date: date | None = None, to_date: date | None = None):
    seed_data()
    hist = COUNTRY_HISTORY.get(iso.upper())
    if not hist:
        raise HTTPException(status_code=404, detail="Country not found")
    rows = hist
    if from_date:
        rows = [r for r in rows if r.date >= from_date]
    if to_date:
        rows = [r for r in rows if r.date <= to_date]
    return rows


@router.get("/countries/{iso}/drivers")
def country_drivers(iso: str, at: date | None = None):
    seed_data()
    hist = COUNTRY_HISTORY.get(iso.upper())
    if not hist:
        raise HTTPException(status_code=404, detail="Country not found")
    if at:
        for row in hist:
            if row.date == at:
                return row.drivers
    return hist[-1].drivers


@router.get("/global/heatmap")
def global_heatmap():
    seed_data()
    return latest_heatmap()


@router.get("/alerts")
def alerts(country: str | None = None, severity: str | None = None):
    seed_data()
    rows = ALERTS
    if country:
        rows = [a for a in rows if a.country == country.upper()]
    if severity:
        rows = [a for a in rows if a.severity == severity]
    return rows


@router.post("/alerts/rules")
def add_alert_rule(rule: AlertRuleIn):
    payload = rule.model_dump()
    payload["id"] = str(uuid4())
    ALERT_RULES.append(payload)
    return payload


@router.post("/portfolio")
def save_portfolio(portfolio: PortfolioIn):
    seed_data()
    portfolio_id = str(uuid4())
    PORTFOLIOS[portfolio_id] = portfolio.model_dump()
    return {"id": portfolio_id, **portfolio.model_dump()}


@router.get("/portfolio/{portfolio_id}/risk", response_model=PortfolioRisk)
def portfolio_risk(portfolio_id: str):
    seed_data()
    p = PORTFOLIOS.get(portfolio_id)
    if not p:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    heat = {h.iso: h for h in latest_heatmap()}
    weights = p["exposures"]
    total = sum(weights.values()) or 1
    weighted_risk = sum((w / total) * heat[iso].risk_score for iso, w in weights.items() if iso in heat)
    top = sorted(
        (heat[iso] for iso in weights if iso in heat),
        key=lambda x: x.risk_score,
        reverse=True,
    )[:3]
    return PortfolioRisk(
        id=portfolio_id,
        weighted_risk_score=round(weighted_risk, 1),
        tail_risk_score=round(min(100, weighted_risk * 1.18), 1),
        top_contributors=top,
    )
