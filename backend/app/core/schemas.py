from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class Driver(BaseModel):
    feature: str
    impact: float


class Subindices(BaseModel):
    macro: float
    credit_stress: float
    bubble: float
    external: float
    geopolitical: float


class CountryLatest(BaseModel):
    country: str
    date: date
    risk_score: float = Field(ge=0, le=100)
    bucket: Literal["Low", "Medium", "High", "Severe"]
    prob_recession_6m: float = Field(ge=0, le=1)
    prob_recession_12m: float = Field(ge=0, le=1)
    subindices: Subindices
    drivers: list[Driver]


class CountryMeta(BaseModel):
    iso: str
    name: str
    region: str


class HeatmapPoint(BaseModel):
    iso: str
    name: str
    risk_score: float
    bucket: str
    wow_change: float


class AlertRuleIn(BaseModel):
    country: str
    trigger_type: Literal["threshold", "delta", "regime_shift"]
    threshold: float | None = None
    lookback_days: int | None = 7


class Alert(BaseModel):
    id: str
    country: str
    date: date
    severity: Literal["info", "warning", "critical"]
    message: str


class PortfolioIn(BaseModel):
    name: str
    exposures: dict[str, float]


class PortfolioRisk(BaseModel):
    id: str
    weighted_risk_score: float
    tail_risk_score: float
    top_contributors: list[HeatmapPoint]
