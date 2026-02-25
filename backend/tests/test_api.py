from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_countries_list():
    resp = client.get('/countries')
    assert resp.status_code == 200
    assert len(resp.json()) >= 5


def test_country_latest_schema():
    resp = client.get('/countries/GRC/latest')
    data = resp.json()
    assert resp.status_code == 200
    assert 0 <= data['risk_score'] <= 100
    assert 'subindices' in data


def test_portfolio_flow():
    create = client.post('/portfolio', json={'name': 'Test', 'exposures': {'GRC': 40, 'BRA': 60}})
    assert create.status_code == 200
    pid = create.json()['id']
    risk = client.get(f'/portfolio/{pid}/risk')
    assert risk.status_code == 200
    assert 'weighted_risk_score' in risk.json()
