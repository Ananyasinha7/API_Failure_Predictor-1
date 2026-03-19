from .config import config
import logging



def setup_logging():
    level_str=(config.LOG_LEVEL or "INFO").upper()
    root_logger_level=logging.getLevelName(level_str)

    if not isinstance(root_logger_level, int): 
        raise ValueError(
            f"Invalid LOG_LEVEL: '{level_str}'. "
            "Only DEBUG, INFO, WARNING, ERROR valid"
        )


    console_handler= logging.StreamHandler()
    console_handler.setLevel(root_logger_level)
    formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    root_logger=logging.getLogger()
    root_logger.setLevel(root_logger_level)
    if not root_logger.hasHandlers():
        root_logger.addHandler(console_handler)
    