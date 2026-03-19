from sklearn.linear_model import LinearRegression
import numpy as np
import logging
import os
from ml_backend.model_utils import save_model

logger = logging.getLogger(__name__)


def create_default_model(model_path):
    try:
        model_dir = os.path.dirname(model_path) or '.'
        os.makedirs(model_dir, exist_ok=True)

        X_dummy = np.array([
            [100, 0.05, 0.5, 2.0, 1.5],
            [200, 0.08, 0.6, 2.5, 1.8],
            [150, 0.03, 0.4, 1.5, 1.0],
            [300, 0.10, 0.7, 3.0, 2.0],
            [250, 0.06, 0.55, 2.2, 1.6]
        ])

        y_dummy = np.array([0.25, 0.40, 0.15, 0.50, 0.30])

        model = LinearRegression()
        model.fit(X_dummy, y_dummy)

        save_model(model, model_path)
        logger.info(f"Created default model at {model_path}")
        return model

    except Exception as e:
        logger.error(f"Failed to create default model: {e}", exc_info=True)
        raise


def ensure_model_exists(model_path):
    if not os.path.isfile(model_path):
        logger.warning(f"Model not found at {model_path}. Creating default model.")
        create_default_model(model_path)
        return True
    return False
