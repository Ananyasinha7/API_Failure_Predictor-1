from ml_backend.dataset_builder import build_training_dataset
from ml_backend.model_utils import save_model
from sklearn.linear_model import LinearRegression
import logging
import os
from sklearn.metrics import mean_squared_error, r2_score

MODEL_VERSION = "1.0.0"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, f"risk_model_v{MODEL_VERSION}.pkl")

logger = logging.getLogger(__name__)


def train_model():
    logger.info("Starting model training")
    dataset_result = build_training_dataset()

    if dataset_result is None or len(dataset_result) < 2:
        logger.warning("No data available for training. Exiting.")
        return

    X, y = dataset_result[0], dataset_result[1]

    if X is None or y is None:
        logger.warning("Training data is None. Exiting.")
        return

    if len(X) < 5:
        logger.warning(f"Too few samples for training: {len(X)} samples")
        return

    logger.info("Dataset loaded successfully")
    logger.info(f"X shape: {X.shape}, y shape: {y.shape}")

    try:
        model = LinearRegression()
        model.fit(X, y)
        logger.info("Model training completed")

        y_pred = model.predict(X)
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        logger.info(f"Training R2 Score: {r2:.4f}")
        logger.info(f"Training MSE: {mse:.6f}")

        save_model(model, MODEL_PATH)
        logger.info(f"Model saved successfully to {MODEL_PATH}")

    except Exception as e:
        logger.error(f"Error during model training: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    train_model()

