import asyncio
from src.core.config import settings
from src.services.model_engine import ModelEngine

async def test_engine():
    print("--- Phase 2 Test: Engine Start ---")
    
    engine = ModelEngine.get_instance()
    engine.load_model()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say 'Phase 2 Complete' and nothing else."}
    ]
    
    print("\nStreaming response:")
    async for chunk in engine.chat(messages, max_tokens=50):
        delta = chunk['choices'][0]['delta']
        if 'content' in delta:
            print(delta['content'], end="", flush=True)
            
    print("\n\n--- Phase 2 Test: Finished ---")

if __name__ == "__main__":
    asyncio.run(test_engine())