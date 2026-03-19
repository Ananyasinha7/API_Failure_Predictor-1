from .config import config
import logging,sys,os

logger=logging.getLogger(__name__)

def check_required_env_vars(req_vars: list[str]):
    missing_vars=[]
    for var in req_vars:
        value=getattr(config, var, None)

        if value is None or (isinstance(value, str) and not value.strip()):
            missing_vars.append(var)

    if missing_vars:
       logger.critical("Startup failed. Missing req env vars: %s",", ".join(missing_vars))
       sys.exit(1)


def check_model_path_exists( description: str):
    if not config.MODEL_PATH:
        logger.critical("Startup failed. MODEL_PATH env var is not set.")
        sys.exit(1)
    if not os.path.isfile(config.MODEL_PATH):
        logger.critical("Startup failed. %s file not found at path: %s", description, config.MODEL_PATH)
        sys.exit(1)
    