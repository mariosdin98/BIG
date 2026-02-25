from datetime import date
from statistics import mean, pstdev

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import AlertEvent, AlertRule, Country, CountrySnapshot, Portfolio
from app.schemas.api import (
    AlertResponse,
    AlertRuleCreate,
    AlertRuleResponse,
    BlackSwanEvent,
    CountryLatestResponse,
    CountryMeta,
    Driver,
    HeatmapPoint,
    PortfolioCreate,
    PortfolioResponse,
    PortfolioRiskResponse,
    Subindices,
)

router = APIRouter()


def _latest_snapshot(db: Session, iso: str) -> CountrySnapshot | None:
    return (
        db.execute(
            select(CountrySnapshot)
            .where(CountrySnapshot.country_iso == iso)
            .order_by(CountrySnapshot.date.desc())
        )
        .scalars()
        .first()
    )


def _build_heatmap_points(db: Session) -> list[HeatmapPoint]:
    countries = db.execute(select(Country)).scalars().all()
    raw_points: list[dict] = []

    for country in countries:
        latest = db.execute(
            select(CountrySnapshot)
            .where(CountrySnapshot.country_iso == country.iso)
            .order_by(CountrySnapshot.date.desc())
        ).scalars().first()
        if not latest:
            continue

        prev = db.execute(
            select(CountrySnapshot)
            .where(
                CountrySnapshot.country_iso == country.iso,
                CountrySnapshot.date < latest.date,
            )
            .order_by(CountrySnapshot.date.desc())
        ).scalars().first()
        weekly_delta = latest.risk_score - (prev.risk_score if prev else latest.risk_score)

        raw_points.append(
            {
                "iso": country.iso,
                "name": country.name,
                "risk_score": latest.risk_score,
                "bucket": latest.bucket,
                "weekly_delta": round(weekly_delta, 2),
            }
        )

    deltas = [point["weekly_delta"] for point in raw_points]
    delta_mean = mean(deltas) if deltas else 0.0
    delta_std = pstdev(deltas) if len(deltas) > 1 else 0.0

    points: list[HeatmapPoint] = []
    for point in raw_points:
        zscore = ((point["weekly_delta"] - delta_mean) / delta_std) if delta_std else 0.0
        black_swan = zscore >= 2.0 and point["risk_score"] >= 65.0
        points.append(HeatmapPoint(**point, black_swan_signal=black_swan))

    return sorted(points, key=lambda x: x.risk_score, reverse=True)


@router.get("/countries", response_model=list[CountryMeta])
def list_countries(db: Session = Depends(get_db)):
    return db.execute(select(Country).order_by(Country.name)).scalars().all()


@router.get("/countries/{iso}/latest", response_model=CountryLatestResponse)
def latest_country(iso: str, db: Session = Depends(get_db)):
    snap = _latest_snapshot(db, iso.upper())
    if not snap:
        raise HTTPException(status_code=404, detail="Country snapshot not found")

    return CountryLatestResponse(
        country=snap.country_iso,
        date=snap.date,
        risk_score=snap.risk_score,
        bucket=snap.bucket,
        prob_recession_6m=snap.prob_recession_6m,
        prob_recession_12m=snap.prob_recession_12m,
        subindices=Subindices(
            macro=snap.macro,
            credit_stress=snap.credit_stress,
            bubble=snap.bubble,
            external=snap.external,
            geopolitical=snap.geopolitical,
        ),
        drivers=[Driver(**d) for d in snap.drivers],
    )


@router.get("/countries/{iso}/history")
def country_history(
    iso: str,
    from_date: date | None = Query(default=None, alias="from"),
    to: date | None = None,
    db: Session = Depends(get_db),
):
    conditions = [CountrySnapshot.country_iso == iso.upper()]
    if from_date:
        conditions.append(CountrySnapshot.date >= from_date)
    if to:
        conditions.append(CountrySnapshot.date <= to)

    snaps = db.execute(
        select(CountrySnapshot)
        .where(and_(*conditions))
        .order_by(CountrySnapshot.date.asc())
    ).scalars().all()

    return [
        {
            "date": s.date,
            "risk_score": s.risk_score,
            "prob_recession_6m": s.prob_recession_6m,
            "prob_recession_12m": s.prob_recession_12m,
            "subindices": {
                "macro": s.macro,
                "credit_stress": s.credit_stress,
                "bubble": s.bubble,
                "external": s.external,
                "geopolitical": s.geopolitical,
            },
        }
        for s in snaps
    ]


@router.get("/countries/{iso}/drivers")
def country_drivers(iso: str, date_value: date | None = Query(default=None, alias="date"), db: Session = Depends(get_db)):
    query = select(CountrySnapshot).where(CountrySnapshot.country_iso == iso.upper())
    if date_value:
        query = query.where(CountrySnapshot.date == date_value)
    snap = db.execute(query.order_by(CountrySnapshot.date.desc())).scalars().first()
    if not snap:
        raise HTTPException(status_code=404, detail="Drivers not found")
    return {"country": iso.upper(), "date": snap.date, "drivers": snap.drivers}


@router.get("/global/heatmap", response_model=list[HeatmapPoint])
def global_heatmap(db: Session = Depends(get_db)):
    return _build_heatmap_points(db)


@router.get("/global/black-swans", response_model=list[BlackSwanEvent])
def global_black_swans(db: Session = Depends(get_db)):
    points = _build_heatmap_points(db)
    deltas = [point.weekly_delta for point in points]
    delta_mean = mean(deltas) if deltas else 0.0
    delta_std = pstdev(deltas) if len(deltas) > 1 else 0.0

    events: list[BlackSwanEvent] = []
    for point in points:
        if not point.black_swan_signal:
            continue
        zscore = ((point.weekly_delta - delta_mean) / delta_std) if delta_std else 0.0
        events.append(
            BlackSwanEvent(
                iso=point.iso,
                name=point.name,
                risk_score=point.risk_score,
                weekly_delta=point.weekly_delta,
                zscore_delta=round(zscore, 2),
            )
        )
    return events


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    country: str | None = None,
    severity: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(AlertEvent)
    if country:
        query = query.where(AlertEvent.country_iso == country.upper())
    if severity:
        query = query.where(AlertEvent.severity == severity)
    return db.execute(query.order_by(AlertEvent.created_at.desc())).scalars().all()


@router.post("/alerts/rules", response_model=AlertRuleResponse)
def create_alert_rule(payload: AlertRuleCreate, db: Session = Depends(get_db)):
    rule = AlertRule(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/portfolio", response_model=PortfolioResponse)
def create_portfolio(payload: PortfolioCreate, db: Session = Depends(get_db)):
    portfolio = Portfolio(**payload.model_dump())
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)
    return portfolio


@router.get("/portfolio/{portfolio_id}/risk", response_model=PortfolioRiskResponse)
def portfolio_risk(portfolio_id: int, db: Session = Depends(get_db)):
    portfolio = db.get(Portfolio, portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    weighted = 0.0
    weights_sum = 0.0
    for position in portfolio.exposures:
        iso = position.get("iso", "").upper()
        weight = float(position.get("weight", 0))
        snap = _latest_snapshot(db, iso)
        if not snap:
            continue
        weighted += snap.risk_score * weight
        weights_sum += weight

    weighted_risk = weighted / weights_sum if weights_sum else 0.0
    tail_risk = min(100.0, weighted_risk * 1.2)

    return PortfolioRiskResponse(
        portfolio_id=portfolio_id,
        weighted_risk=round(weighted_risk, 2),
        tail_risk=round(tail_risk, 2),
        exposures_count=len(portfolio.exposures),
    )
