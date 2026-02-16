import asyncio
from typing import Dict, List, Generator, Optional
from llama_cpp import Llama
from src.core.config import settings
from src.core.logging import logger

# ModelEngine: A singleton wrapper around llama.cpp library, handles model loading, configuration, and thread safe inference
# load_model: loads the model into the memory
# chat: It works on the openAi's method of chat, the self lock is for multiple users, it will creat a queue. 

class ModelEngine:
    _instance: Optional["ModelEngine"] = None

    def __init__(self):
        self.llm: Optional[Llama] = None
        self.lock = asyncio.Lock()

    @classmethod
    def get_instance(cls) -> "ModelEngine":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self):

        if self.llm is not None:
            logger.warning("Model is already loaded.")
            return

        logger.info(f"Loading model from: {settings.model.path} ...")
        
        try:
            self.llm = Llama(
                model_path=settings.model.path,
                n_ctx=settings.model.context_size,
                n_threads=settings.model.n_threads,
                n_gpu_layers=settings.model.n_gpu_layers,
                use_mmap=settings.model.use_mmap,
                use_mlock=settings.model.use_mlock,
                verbose=True  
            )
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.critical(f"Failed to load model: {e}")
            raise e

    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> Generator[Dict, None, None]:
        if not self.llm:
            raise RuntimeError("Model is not loaded. Call load_model() first.")

        async with self.lock:
            logger.debug("Lock acquired. Starting generation...")

            stream = self.llm.create_chat_completion(
                messages=messages,
                stream=True,
                **kwargs
            )
            
            for chunk in stream:
                yield chunk
                await asyncio.sleep(0)
            
            logger.debug("Generation complete. Releasing lock.")