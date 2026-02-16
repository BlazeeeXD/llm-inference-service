from src.core.config import settings
from src.core.logging import logger

def test_setup():
    logger.info("Starting Phase 1 Verification...")
    
    logger.info(f"Server Host: {settings.server.host}")
    logger.info(f"Model Path: {settings.model.path}")
    logger.info(f"GPU Layers: {settings.model.n_gpu_layers}")
    
    if settings.model.context_size > 0:
        logger.info("Context size is valid.")
    else:
        logger.error("Context size is invalid!")

if __name__ == "__main__":
    test_setup()