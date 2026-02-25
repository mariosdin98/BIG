# Crisis Radar

MVP πλατφόρμα έγκαιρης προειδοποίησης για country-level crisis risk με:
- **Risk Score (0-100)** και bucket
- **Recession probabilities** (6m / 12m)
- **Subindices** (macro, credit stress, bubble, external, geopolitical)
- **Explainability drivers**
- **Global world heatmap + charts**
- **Black swan anomaly signals**

## Τι βελτιώθηκε (για να είναι πιο σοβαρό)
- Τώρα το ingestion τραβάει **catalog από όλες τις χώρες** (μη-aggregate) από World Bank API.
- Οι indicators τραβιούνται σε bulk ανά indicator (`country/all/indicator/...`) για σταθερότητα.
- Υπάρχει deterministic fallback όταν το network/source δεν είναι διαθέσιμο.
- Προστέθηκε endpoint `GET /global/black-swans` με z-score ανίχνευση ακραίων εβδομαδιαίων μεταβολών.

## Methodology (research-grounded)
Το scoring στηρίζεται σε βιβλιογραφικά robust μοτίβα:
- **Early warning indicators** για κρίσεις (Kaminsky, Lizondo, Reinhart; Berg & Pattillo frameworks)
- **Credit/GDP gap & macro-financial imbalances** (BIS literature: Borio/Drehmann)
- **Systemic stress / regime shifts** με ανάλυση ανωμαλιών (z-score EVT-style proxy για MVP)

> Στο MVP χρησιμοποιείται deterministic proxy μοντελοποίηση για να λειτουργεί end-to-end. Στο επόμενο στάδιο μπαίνουν πλήρη ML models (logit/boosting/calibration) και paid market feeds.

## Πώς το τρέχεις στο GitHub
### Option A — GitHub Codespaces
1. Push το repo στο GitHub.
2. `Code → Codespaces → Create codespace on main`.
3. Terminal 1:
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
4. Terminal 2:
```bash
cd frontend
npm install
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000 npm run dev -- --hostname 0.0.0.0 --port 3000
```
5. Άνοιξε forwarded port `3000`.

### Option B — GitHub Actions
Υπάρχει workflow στο `.github/workflows/ci.yml` που τρέχει compile + tests σε κάθε push/PR στο `main`.

## Deploy αλλού
### Backend + DB
- Deploy `backend/` (Dockerfile έτοιμο)
- Env:
  - `DATABASE_URL=postgresql+psycopg://...`
  - `SKIP_INGEST_ON_STARTUP=false`

### Frontend
- Deploy `frontend/`
- Env:
  - `NEXT_PUBLIC_API_BASE=https://<your-backend-domain>`

### Docker Compose (VPS)
```bash
docker compose up --build
```

## API endpoints (MVP)
- `GET /countries`
- `GET /countries/{iso}/latest`
- `GET /countries/{iso}/history?from=&to=&freq=`
- `GET /countries/{iso}/drivers?date=`
- `GET /global/heatmap`
- `GET /global/black-swans`
- `GET /alerts?country=&severity=&from=`
- `POST /alerts/rules`
- `POST /portfolio`
- `GET /portfolio/{id}/risk`
