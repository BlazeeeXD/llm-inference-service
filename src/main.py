from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sse_starlette.sse import EventSourceResponse
from src.core.config import settings
from src.core.logging import logger
from src.services.model_engine import ModelEngine
from src.schemas.openai_types import ChatCompletionRequest
import json

# Lifecycle Manager: This runs before the server starts accepting requests
# health_check: Simple heartbeat endpoint for Docker/Kubernetes.
# chat_completions: OpenAI-compatible chat completion endpoint, only supports streaming for now.
# stream_generator: Helper to yield data in OpenAI SSE format.
# I am pasting the command here too (It should be on ReadMe too)
#python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Server starting up...")
    try:
        engine = ModelEngine.get_instance()
        engine.load_model()
    except Exception as e:
        logger.critical(f"Startup failed: {e}")
        raise e
    yield 
    logger.info("Server shutting down...")

app = FastAPI(title="LLM Inference Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health_check():
    engine = ModelEngine.get_instance()
    if engine.llm:
        return {"status": "ok", "model": settings.model.path}
    else:
        raise HTTPException(status_code=503, detail="Model not loaded")

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    engine = ModelEngine.get_instance()
    
    messages_dict = [msg.model_dump() for msg in request.messages]

    gen_kwargs = {
        "temperature": request.temperature,
        "top_p": request.top_p,
        "max_tokens": request.max_tokens,
    }

    if request.stream:
        return EventSourceResponse(
            stream_generator(engine, messages_dict, gen_kwargs)
        )
    else:
        raise HTTPException(status_code=400, detail="Only stream=True is supported currently.")

async def stream_generator(engine, messages, kwargs):
    
    generator = engine.chat(messages, **kwargs)
    async for chunk in generator:
        data = json.dumps(chunk)
        yield dict(data=data)

    yield dict(data="[DONE]")