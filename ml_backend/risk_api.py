from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.models import RiskScores
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.schema import RiskScoreResponse, RiskSummaryResponse
import logging
from fastapi.security.api_key import APIKeyHeader
from ml_backend.train_model import MODEL_VERSION
from backend.config import config

app = FastAPI()


logger = logging.getLogger(__name__)

APP_START_TIME = datetime.utcnow()


RISK_API_KEY = config.RISK_API_KEY or "default_risk_api_key"


limit_per_minute = 60
request_counts_per_key = {}


def verify_api_key(x_api_key: str = Depends(APIKeyHeader(name="X-API-KEY"))):
    if x_api_key is None:
        logger.warning("API request made without API key")
        raise HTTPException(status_code=401, detail="Api key missing")
    if x_api_key != RISK_API_KEY:
        logger.warning("API request made with invalid API key")
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return x_api_key


def rate_limiter(x_api_key: str = Depends(verify_api_key)):
    current_time = datetime.utcnow()
    entry = request_counts_per_key.get(
        x_api_key,
        {"count": 0, "timestamp": current_time}
    )
    elapsed = (current_time - entry["timestamp"]).total_seconds()
    if elapsed > 60:
        entry["count"] = 0
        entry["timestamp"] = current_time
    if entry["count"] >= limit_per_minute:
        logger.warning("Rate limit exceeded for API key")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    entry["count"] += 1
    request_counts_per_key[x_api_key] = entry


@app.get("/health", response_model=dict)
def health_check():
    return {"status": "ok"}

@app.get("/risk/latest", response_model=List[RiskScoreResponse])
def get_latest_risk_scores(
    minutes: int = 10,
    db: Session = Depends(get_db),
    limit: int = 100,
    APIKEY=Depends(verify_api_key),
    rate_limit=Depends(rate_limiter)
):
    try:
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        latest_risks = db.query(RiskScores).filter(
            RiskScores.created_at >= cutoff
        ).order_by(RiskScores.created_at.desc()).limit(limit).all()
        logger.info(f"Retrieved {len(latest_risks)} latest risk scores")
        return latest_risks
    except Exception as e:
        logger.error(f"Error fetching latest risk scores: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/risk/{endpoint}", response_model=RiskScoreResponse)
def get_risk_score(
    endpoint: str,
    db: Session = Depends(get_db),
    APIKEY=Depends(verify_api_key),
    rate_limit=Depends(rate_limiter)
):
    try:
        risk_score = db.query(RiskScores).filter(
            RiskScores.endpoint == endpoint
        ).order_by(RiskScores.created_at.desc()).first()
        if not risk_score:
            logger.info(f"Risk score not found for endpoint: {endpoint}")
            raise HTTPException(status_code=404, detail="Risk score not found")
        return risk_score
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching risk score for endpoint {endpoint}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/risk/summary", response_model=List[RiskSummaryResponse])
def get_summary(
    db: Session = Depends(get_db),
    APIKEY=Depends(verify_api_key),
    rate_limit=Depends(rate_limiter)
):
    try:
        summary = db.query(
            RiskScores.endpoint,
            func.avg(RiskScores.risk_score).label("avg_risk_score"),
            func.max(RiskScores.risk_score).label("max_risk_score"),
            func.min(RiskScores.risk_score).label("min_risk_score")
        ).group_by(RiskScores.endpoint).all()
        logger.info(f"Retrieved risk summary for {len(summary)} endpoints")
        return summary
    except Exception as e:
        logger.error(f"Error fetching risk summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
@app.get("/meta", response_model=dict)
def get_metadata(
    rate_limit=Depends(rate_limiter),
    APIKEY=Depends(verify_api_key)
):
    try:
        metadata = {
            "service": "Risk Prediction API",
            "version": MODEL_VERSION,
            "uptime": (datetime.utcnow() - APP_START_TIME).total_seconds(),
            "server_time": datetime.utcnow().isoformat()
        }
        return metadata
    except Exception as e:
        logger.error(f"Error fetching metadata: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

