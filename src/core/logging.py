import logging
import sys
from src.core.config import settings

# setup_logging: Configurrs the root logger based on settings 
def setup_logging():
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    numeric_level = getattr(logging, settings.server.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout) 
        ]
    )
    
    logger = logging.getLogger("llm_service")
    logger.setLevel(numeric_level)
    
    return logger

logger = setup_logging()