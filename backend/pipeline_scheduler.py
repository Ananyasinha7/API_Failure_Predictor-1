from datetime import datetime, timedelta
from .feature_extraction import extract_features
from ml_backend.train_model import train_model
from ml_backend.predict_risk import predict_and_store_risk
import logging
import time

logger = logging.getLogger(__name__)

WINDOW_MINUTES = 5
TRAINING_INTERVAL_HOURS = 24
CYCLE_SECONDS = WINDOW_MINUTES * 60


def run_pipeline_scheduler():
    last_training_time = datetime(1970, 1, 1)

    while True:
        cycle_start = datetime.utcnow()

        try:
            extract_features_start = datetime.utcnow()
            logger.info("Starting feature extraction")
            extract_features(window_minutes=WINDOW_MINUTES)
            extract_features_end = datetime.utcnow()
            extraction_ok = True
            logger.info(f"Feature extraction completed at {extract_features_end}, duration: {extract_features_end - extract_features_start}")

        except Exception as e:
            logger.error(f"Error during feature extraction: {e}")
            extraction_ok = False

        if extraction_ok:
            try:
                predict_risk_start = datetime.utcnow()
                logger.info("Starting risk prediction")
                predict_and_store_risk()
                predict_risk_end = datetime.utcnow()
                logger.info(f"Risk prediction completed at {predict_risk_end}, duration: {predict_risk_end - predict_risk_start}")
            except Exception as e:
                logger.error(f"Error during risk prediction: {e}")

        if datetime.utcnow() - last_training_time >= timedelta(hours=TRAINING_INTERVAL_HOURS):
            try:
                training_start = datetime.utcnow()
                logger.info("Starting model training")
                train_model()
                training_end = datetime.utcnow()
                last_training_time = training_end
                logger.info(f"Model training completed at {training_end}, duration: {training_end - training_start}")
            except Exception as e:
                logger.error(f"Error during model training: {e}")

        cycle_end = datetime.utcnow()
        elapsed = (cycle_end - cycle_start).total_seconds()
        sleep_time = max(0, CYCLE_SECONDS - elapsed)
        logger.info(f"Pipeline cycle completed at {cycle_end}, total duration: {elapsed}")

        time.sleep(sleep_time)


if __name__ == "__main__":
    run_pipeline_scheduler()
  



        

