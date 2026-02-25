# Crisis Radar (MVP)

FastAPI + Next.js platform for early warning signals on macro/financial crisis risk by country.

## What is included

- Country Risk Score (0-100) + bucket (Low/Medium/High/Severe)
- Recession probabilities (6m, 12m)
- Subindices: macro, credit stress, bubble, external, geopolitical
- Explainability drivers (top features)
- Alerts feed and alert-rule creation endpoint
- Portfolio risk endpoint
- Global heatmap + ranking UI + country profile pages
- MVP data ingestion example from World Bank API

## Run

```bash
docker compose up
```

Then open:
- API: http://localhost:8000/docs
- Frontend: http://localhost:3000

## API endpoints

- `GET /countries`
- `GET /countries/{iso}/latest`
- `GET /countries/{iso}/history`
- `GET /countries/{iso}/drivers`
- `GET /global/heatmap`
- `GET /alerts`
- `POST /alerts/rules`
- `POST /portfolio`
- `GET /portfolio/{id}/risk`

## Testing

```bash
cd backend
pip install -r requirements.txt
pytest
```

## Notes

- Current model/scoring is deterministic seeded data + weighted composite to keep MVP self-contained.
- `backend/scripts/ingest_worldbank.py` demonstrates pulling public macro data to extend ingestion.
