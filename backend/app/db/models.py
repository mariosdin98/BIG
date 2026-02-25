from sqlalchemy import JSON, Column, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Country(Base):
    __tablename__ = "countries"

    iso = Column(String(3), primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    region = Column(String(120), nullable=True)

    snapshots = relationship("CountrySnapshot", back_populates="country", cascade="all, delete-orphan")


class CountrySnapshot(Base):
    __tablename__ = "country_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    country_iso = Column(String(3), ForeignKey("countries.iso"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    risk_score = Column(Float, nullable=False)
    bucket = Column(String(20), nullable=False)
    prob_recession_6m = Column(Float, nullable=False)
    prob_recession_12m = Column(Float, nullable=False)

    macro = Column(Float, nullable=False)
    credit_stress = Column(Float, nullable=False)
    bubble = Column(Float, nullable=False)
    external = Column(Float, nullable=False)
    geopolitical = Column(Float, nullable=False)

    drivers = Column(JSON, nullable=False, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    country = relationship("Country", back_populates="snapshots")


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    country_iso = Column(String(3), nullable=True)
    metric = Column(String(50), nullable=False)
    operator = Column(String(10), nullable=False)
    threshold = Column(Float, nullable=False)


class AlertEvent(Base):
    __tablename__ = "alert_events"

    id = Column(Integer, primary_key=True, index=True)
    country_iso = Column(String(3), nullable=False, index=True)
    severity = Column(String(20), nullable=False)
    message = Column(String(500), nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    exposures = Column(JSON, nullable=False, default=list)
