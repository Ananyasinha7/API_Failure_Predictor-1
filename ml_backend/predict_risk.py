from backend.database import SessionLocal
from backend.models import RiskScores, APIFeatures
from ml_backend.model_utils import load_model, validate_risk_score
import logging
from datetime import datetime
from ml_backend.train_model import MODEL_VERSION, MODEL_PATH
from backend.config import config

logger = logging.getLogger(__name__)


def predict_and_store_risk():
    logger.info("Starting risk score prediction and storage")
    db = None
    try:
        db = SessionLocal()

        model = load_model(config.MODEL_PATH)
        if model is None:
            logger.error("Model could not be loaded. Aborting prediction.")
            return

        last_risk_record = db.query(RiskScores).order_by(RiskScores.created_at.desc()).first()
        last_time = datetime(1970, 1, 1)
        if last_risk_record:
            last_time = last_risk_record.created_at

        features = db.query(APIFeatures).filter(APIFeatures.created_at > last_time).order_by(APIFeatures.created_at.asc()).all()

        if not features:
            logger.info("No new features to predict")
            return

        for feature in features:
            try:
                risk_prediction = model.predict([[
                    feature.total_requests,
                    feature.error_rate,
                    feature.avg_response_time,
                    feature.max_response_time,
                    feature.p95_response_time
                ]])

                risk_score = float(risk_prediction[0])
                validated_score = validate_risk_score(risk_score)

                if validated_score is None:
                    logger.warning(f"Invalid risk score {risk_score} for endpoint {feature.endpoint}")
                    continue

                risk_entry = RiskScores(
                    service_name=feature.service_name,
                    endpoint=feature.endpoint,
                    window_start=feature.window_start,
                    risk_score=validated_score,
                    model_version=MODEL_VERSION,
                    created_at=datetime.utcnow()
                )
                db.add(risk_entry)
            except Exception as e:
                logger.error(f"Error predicting risk for feature {feature.endpoint}: {e}")
                continue

        db.commit()
        logger.info(f"Risk prediction and storage completed. Processed {len(features)} features")

    except Exception as e:
        if db:
            db.rollback()
        logger.error(f"Error during risk prediction and storage: {e}", exc_info=True)

    finally:
        if db:
            db.close()

    
    
    

    

