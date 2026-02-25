import os
from datetime import date

os.environ["SKIP_INGEST_ON_STARTUP"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./test_crisis_radar.db"

from fastapi.testclient import TestClient

from app.db.database import Base, SessionLocal, engine
from app.db.models import Country, CountrySnapshot
from app.main import app


client = TestClient(app)


def _seed_minimal_data() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.get(Country, "GRC"):
            db.add(Country(iso="GRC", name="Greece", region="Europe"))
            db.add(
                CountrySnapshot(
                    country_iso="GRC",
                    date=date(2026, 2, 25),
                    risk_score=68.4,
                    bucket="High",
                    prob_recession_6m=0.22,
                    prob_recession_12m=0.41,
                    macro=55.1,
                    credit_stress=72.3,
                    bubble=61.0,
                    external=64.2,
                    geopolitical=58.8,
                    drivers=[{"feature": "yield_curve_slope", "impact": 0.12}],
                )
            )
            db.commit()
    finally:
        db.close()


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_heatmap_endpoint():
    _seed_minimal_data()
    response = client.get('/global/heatmap')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'iso' in data[0]
    assert 'black_swan_signal' in data[0]
