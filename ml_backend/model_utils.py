import pickle
import os
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


def save_model(model, model_path):
    os.makedirs(os.path.dirname(model_path) or '.', exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    logger.info(f"Model saved to {model_path}")
    return True


def load_model(model_path):
    if not os.path.exists(model_path):
        logger.error(f"Model file not found at {model_path}")
        return None
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        logger.info(f"Model loaded from {model_path}")
        return model
    except Exception as e:
        logger.error(f"Error loading model from {model_path}: {e}")
        return None


def validate_risk_score(score):
    if not isinstance(score, (int, float)):
        return None
    bounded_score = max(0.0, min(1.0, float(score)))
    return bounded_score


def normalize_features(features):
    if features is None or len(features) == 0:
        return None
    try:
        features_array = np.array(features)
        if features_array.size == 0:
            return None
        return features_array
    except Exception as e:
        logger.error(f"Error normalizing features: {e}")
        return None


def safe_divide(numerator, denominator, default=0):
    if denominator == 0 or denominator is None:
        return default
    try:
        return float(numerator) / float(denominator)
    except (ValueError, TypeError):
        return default


def compute_composite_risk(error_rate, avg_response_time, max_response_time,
                          p95_response_time, total_requests, max_total_requests):
    if max_total_requests is None or max_total_requests == 0:
        max_total_requests = 1

    try:
        score = (
            0.5 * max(0, min(error_rate, 1)) +
            0.2 * safe_divide(avg_response_time, max_response_time, 0) +
            0.2 * safe_divide(p95_response_time, max_response_time, 0) +
            0.1 * safe_divide(total_requests, max_total_requests, 0)
        )
        return max(0.0, min(1.0, score))
    except Exception as e:
        logger.error(f"Error computing composite risk: {e}")
        return 0.0


def get_model_metadata(model):
    metadata = {
        'created_at': datetime.utcnow().isoformat(),
        'type': type(model).__name__ if model else None,
        'coef_count': len(model.coef_) if hasattr(model, 'coef_') else None,
        'intercept': float(model.intercept_) if hasattr(model, 'intercept_') else None
    }
    return metadata
