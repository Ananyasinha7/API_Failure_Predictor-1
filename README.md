# APIFailure-Predictor

ML system that predicts API endpoint failure risk (0.0-1.0 score) by analyzing error rates, response times, and request volumes.

## The Idea

APIs degrade over time. This pipeline continuously monitors endpoints and scores them, enabling early detection of degradation.

## Use Cases

- **SRE/DevOps Teams** - Proactive alerting before endpoints fail completely. Risk scores trigger automatic scaling or incident response.
- **API Gateway Monitoring** - Monitor third-party or microservice endpoints. Block high-risk calls or route to fallback services.
- **Performance Budgeting** - Track risk score trends. Identify endpoints that need optimization or resource allocation.
- **Load Testing** - Identify which endpoints degrade under load. Use risk scores as baselines for performance regression testing.
- **Incident Prevention** - Historical risk patterns reveal degradation cycles. Schedule maintenance before predicted failures.
- **Multi-tenant Systems** - Per-endpoint risk scoring shows which tenants or features impact overall API health.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         HTTP Requests                               │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     ▼ (continuous)
             ┌──────────────────┐
             │  Main API (8000) │
             │  Logging Mid.    │
             └────────┬─────────┘
                      │
                      ▼
           ┌────────────────────────┐
           │  PostgreSQL: Logs      │
           │  (every request)       │
           └────────┬───────────────┘
                    │
                    │ every 5min
                    ▼
           ┌────────────────────────┐
           │  Feature Extraction    │
           │  (aggregate metrics)   │
           └────────┬───────────────┘
                    │
                    ▼
           ┌────────────────────────┐
           │  PostgreSQL: Features  │
           │  (endpoint metrics)    │
           └────────┬───────────────┘
                    │
                    │ immediate
                    ▼
           ┌────────────────────────┐
           │  Risk Prediction      │
           │  (ML model scores)     │
           └────────┬───────────────┘
                    │
                    ▼
           ┌────────────────────────┐
           │  PostgreSQL: Scores    │
           │  (risk per endpoint)   │
           └────────┬───────────────┘
                    │
         ┌──────────┴──────────┐
         │ every 24hrs         │ on-demand
         ▼                     ▼
    ┌──────────┐        ┌──────────────┐
    │ Retrain  │        │ Risk API     │
    │ Model    │        │ (port 8001)  │
    └──────────┘        │ - Predictions│
                        │ - Summaries  │
                        └──────────────┘
```

**Pipeline:**
1. **Logging** - HTTP middleware → PostgreSQL (endpoint, status_code, response_time)
2. **Features** - 5-min: aggregate total_requests, error_rate, avg/max/p95_response_time
3. **Predict** - LinearRegression: score each endpoint 0.0-1.0
4. **Retrain** - Daily: update model from 6-hour history

## Quick Start

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Create .env
echo "APP_ENV=dev
LOG_LEVEL=INFO
SQLALCHEMY_DATABASE_URL=postgresql://user:password@localhost:5432/api_failure_db
RISK_API_KEY=your-secret
MODEL_PATH=./models/risk_model.pkl" > .env

# Terminal 1
uvicorn backend.main:app --reload

# Terminal 2
python -m backend.pipeline_scheduler

# Terminal 3
uvicorn ml_backend.risk_api:app
```

## API Examples

```bash
# Generate logs
curl http://localhost:8000/           # ok (200)
curl http://localhost:8000/slow       # slow (2s)
curl http://localhost:8000/failure    # error (500)

# Get predictions
curl -H "X-API-KEY: $KEY" http://localhost:8001/risk/latest
curl -H "X-API-KEY: $KEY" http://localhost:8001/risk/summary
curl http://localhost:8001/health
```

## Code Structure

```
APIFailure-Predictor/
├── backend/                    Main API + logging + orchestration
│   ├── main.py                FastAPI app with startup events
│   ├── config.py              Environment configuration loader
│   ├── database.py            SQLAlchemy ORM setup
│   ├── models.py              Database models (Logs, APIFeatures, RiskScores)
│   ├── schema.py              Pydantic response schemas
│   ├── startup_checks.py      Environment validation
│   ├── logging_config.py       Python logging configuration
│   ├── logging_middleware.py   Request/response logging middleware
│   ├── raw_logs.py            File-based logger with rotation
│   ├── feature_extraction.py   Metrics aggregation (5-min windows)
│   └── pipeline_scheduler.py   Main orchestrator (extraction → prediction → training)
│
├── ml_backend/                Training + prediction + serving
│   ├── train_model.py         LinearRegression model training
│   ├── predict_risk.py        Risk score prediction & storage
│   ├── risk_api.py            FastAPI risk prediction endpoint (port 8001)
│   ├── dataset_builder.py     Training dataset preparation
│   ├── model_utils.py         Model I/O, validation, serialization
│   └── model_initialization.py Auto-generate default model on startup
│
├── models/                    Trained model storage
│   └── risk_model.pkl         Serialized scikit-learn model
│
├── logs/                      Application logs
│
├── Dockerfile                 Container image definition
├── docker-compose.yml         Multi-service orchestration
├── requirements.txt           Python dependencies
├── .env                       Environment variables (database, API key, etc.)
├── .gitignore                 Git ignore patterns
├── applications.md            Real-world use cases (gitignored)
└── README.md                  This file
```

**Key Modules:**
- **backend.main** - FastAPI entry point with middleware, startup checks, test endpoints
- **backend.pipeline_scheduler** - Infinite loop orchestrating the entire ML pipeline
- **ml_backend.risk_api** - Separate FastAPI app serving predictions with authentication
- **ml_backend.model_utils** - Utilities for model persistence, validation, and normalization

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Separate APIs (8000, 8001) | Risk API scales independently, cacheable |
| 5-min windows | Balance responsiveness vs noise |
| LinearRegression | Fast, interpretable, needs no GPU |
| Async retraining (24h) | Never blocks predictions, adapts to drift |

## Docker

Run all services with: `docker-compose up -d`. Includes PostgreSQL, Main API (8000), Pipeline Scheduler, and Risk API (8001).

## Troubleshooting

| Error | Fix |
|-------|-----|
| DB not found | `CREATE DATABASE api_failure_db;` |
| Model not loading | App auto-creates default model on first start |
| No features | Wait 5+ min for first extraction cycle |


