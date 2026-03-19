import logging
from logging.handlers import RotatingFileHandler
import os

os.makedirs("logs", exist_ok=True) 

log_file_path = os.path.join(os.path.dirname(__file__),"logs", "api_failure_logs.log") 
logger = logging.getLogger("api_failure_logger")
logger.setLevel(logging.INFO)
handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)

