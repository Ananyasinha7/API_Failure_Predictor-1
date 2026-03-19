from sqlalchemy.orm import Session
from backend.models import APIFeatures
from backend.database import SessionLocal
import pandas as pd
import logging
from datetime import datetime, timedelta
from numpy import clip

logger = logging.getLogger(__name__)


def build_training_dataset(hours: int = 6):
    db = SessionLocal()
    try:
        start_time = datetime.utcnow() - timedelta(hours=hours)
        features = db.query(APIFeatures).filter(APIFeatures.created_at >= start_time).order_by(APIFeatures.created_at.asc()).all()

        if not features:
            logger.info(f"No features found in the last {hours} hours")
            return None, None, start_time, datetime.utcnow()

        max_total_requests = max([feature.total_requests for feature in features]) if features else 1
        if max_total_requests == 0 or max_total_requests is None:
            max_total_requests = 1

        logger.info(f"Max total requests in window: {max_total_requests}")

        data = []
        for feature in features:
            data.append([
                feature.service_name,
                feature.endpoint,
                feature.total_requests,
                feature.error_rate,
                feature.avg_response_time,
                feature.max_response_time,
                feature.p95_response_time
            ])

        df = pd.DataFrame(data, columns=[
            "service_name",
            "endpoint",
            "total_requests",
            "error_rate",
            "avg_response_time",
            "max_response_time",
            "p95_response_time"
        ])

        def safe_divide(a, b):
            return a / b if b != 0 else 0

        risk = []
        for i, row in df.iterrows():
            score = (
                0.5 * row['error_rate'] +
                0.2 * safe_divide(row['avg_response_time'], row['max_response_time']) +
                0.2 * safe_divide(row['p95_response_time'], row['max_response_time']) +
                0.1 * safe_divide(row['total_requests'], max_total_requests)
            )
            risk.append(min(max(score, 0), 1))

        df['risk_score'] = risk
        X = df.drop(columns=['service_name', 'endpoint', 'risk_score'])
        y = df['risk_score']

        logger.info(f"Dataset built successfully: {len(df)} rows")
        logger.info(f"X shape: {X.shape}, y shape: {y.shape}")
        logger.info(f"Sample X:\n{X.head(3)}")
        logger.info(f"Sample y:\n{y.head(3)}")

        return X, y, start_time, datetime.utcnow()

    except Exception as e:
        logger.error(f"Error building training dataset: {e}", exc_info=True)
        return None, None, start_time if 'start_time' in locals() else None, datetime.utcnow() if 'e' in locals() else None

    finally:
        db.close()



        




        
      