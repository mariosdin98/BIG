from datetime import date, datetime
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


class CountryLatestResponse(BaseModel):
    country: str
    date: date
    risk_score: float
    bucket: str
    prob_recession_6m: float
    prob_recession_12m: float
    subindices: Subindices
    drivers: list[Driver]


class CountryMeta(BaseModel):
    iso: str
    name: str
    region: str | None = None


class HeatmapPoint(BaseModel):
    iso: str
    name: str
    risk_score: float
    bucket: str
    weekly_delta: float
    black_swan_signal: bool = False


class BlackSwanEvent(BaseModel):
    iso: str
    name: str
    risk_score: float
    weekly_delta: float
    zscore_delta: float


class AlertRuleCreate(BaseModel):
    name: str
    country_iso: str | None = None
    metric: str = Field(default="risk_score")
    operator: str = Field(default=">")
    threshold: float


class AlertRuleResponse(AlertRuleCreate):
    id: int


class AlertResponse(BaseModel):
    id: int
    country_iso: str
    severity: str
    message: str
    metadata: dict
    created_at: datetime


class PortfolioCreate(BaseModel):
    name: str
    exposures: list[dict]


class PortfolioResponse(BaseModel):
    id: int
    name: str
    exposures: list[dict]


class PortfolioRiskResponse(BaseModel):
    portfolio_id: int
    weighted_risk: float
    tail_risk: float
    exposures_count: int
