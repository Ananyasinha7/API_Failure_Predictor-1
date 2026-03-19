from datetime import datetime, timedelta
from .models import APIFeatures, Logs
from sqlalchemy.orm import Session
from .database import SessionLocal
from sqlalchemy import func, Integer, Float, String, cast
import logging

logger = logging.getLogger(__name__)

def extract_features(window_minutes: int = 5):
    db = SessionLocal()
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=window_minutes)
    try:
        query = db.query(
            Logs.service_name,
            Logs.endpoint,
            func.count().label("total_requests"),
            func.sum(func.cast(Logs.status_code>=500, Integer)).label("error_count"),
            func.cast(func.sum(func.cast(Logs.status_code>=500, Integer)), Float) / func.nullif(func.count(),0).label("error_rate"),
            func.avg(Logs.response_time).label("avg_response_time"),
            func.max(Logs.response_time).label("max_response_time"),
            func.percentile_cont(0.95).within_group(Logs.response_time).label("p95_response_time")
        ).filter(
            Logs.timestamp>=start_time,
            Logs.timestamp<end_time
        ).group_by(Logs.service_name, Logs.endpoint)
        results = query.all()
        if not results:
            logger.info("No logs found in the specified time window.")
            return
        for row in results:
            feature_entry = APIFeatures(
                service_name=row.service_name,
                endpoint=row.endpoint,
                window_start=start_time,
                window_end=end_time,
                total_requests=row.total_requests,
                error_count=row.error_count,
                error_rate=row.error_rate,
                avg_response_time=row.avg_response_time,
                max_response_time=row.max_response_time,
                p95_response_time=row.p95_response_time
            )
            db.add(feature_entry)
        db.commit()
        logger.info(f"Feature extraction completed: {len(results)} features extracted")

    except Exception as e:
        db.rollback()
        logger.error(f"Error extracting features: {e}", exc_info=True)
    finally:
        db.close()


