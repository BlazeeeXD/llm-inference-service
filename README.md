# LLM Inference Service  
### Local OpenAI-Compatible Inference Server Built on llama.cpp

A hardware-aware, concurrency-safe inference service that exposes locally hosted `.gguf` language models through an **OpenAI-compatible REST API**.

This project demonstrates backend architecture, lifecycle management, concurrency control, and streaming API design — implemented using FastAPI and `llama-cpp-python`.

Designed to run entirely on local infrastructure (CPU or GPU) and serve multiple clients over a private network.

---

## Why This Exists

Most local LLM tools (CLI runners, GUI wrappers, desktop apps) are:

- Not OpenAI API compatible  
- Not designed for multi-client access  
- Not concurrency-safe  
- Not lifecycle-aware  
- Difficult to integrate into larger backend systems  

This project provides:

- A clean HTTP interface  
- Deterministic request handling  
- Safe queued execution  
- Real-time token streaming  
- Strict configuration validation  

It is not a GUI tool.  
It is a backend inference service.

---

## Design Goals

- **OpenAI API Compatibility** — Drop-in replacement for `/v1/chat/completions`
- **Concurrency Safety** — Prevent model state corruption under parallel requests
- **Lifecycle Control** — Load model before accepting traffic
- **Streaming First** — Server-Sent Events for real-time token delivery
- **Hardware Awareness** — Configurable GPU offloading and thread tuning
- **Fail Fast Configuration** — Strict YAML validation via Pydantic

---

## System Architecture

### Execution Flow

1. Client sends POST request to `/v1/chat/completions`
2. Request enters async mutex queue
3. `ModelEngine` acquires exclusive execution lock
4. `llama-cpp-python` performs inference
5. Tokens stream back via SSE (`text/event-stream`)
6. Lock is released for next queued request

### Architectural Characteristics

- Single model instance (singleton pattern)
- Global async mutex for serialized inference
- Streaming responses via `sse-starlette`
- Strict config validation at boot
- Preload model before binding network port

This prevents:

- Race conditions
- VRAM corruption
- Partial initialization failures
- Silent misconfiguration

---

## Core Features

- OpenAI-compatible `/v1/chat/completions`
- Real-time streaming token output
- Async request queue using `asyncio.Lock`
- YAML-driven configuration
- Structured logging
- Health check endpoint
- GPU layer offloading support
- Memory mapping (`mmap`) support

---

## Tech Stack

- **Language:** Python 3.10+
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Inference Backend:** llama-cpp-python
- **Streaming:** sse-starlette
- **Validation:** Pydantic
- **Configuration:** YAML

---

## Project Structure

```
llm-inference-service/
├── config/
│   └── config.yaml
├── models/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   │   └── openai_types.py
│   └── services/
│       └── model_engine.py
├── requirements.txt
└── test_f3.py
```

---

## Installation

### Prerequisites

- Python 3.10+
- C++ compiler (required to build llama-cpp bindings)
- A `.gguf` model file

---

### Setup

Clone the repository:

```bash
git clone https://github.com/yourusername/llm-inference-service.git
cd llm-inference-service
```

Create virtual environment:

```bash
python -m venv .venv
```

Activate environment:

**Windows**
```bash
.venv\Scripts\activate
```

**Mac/Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

Edit `config/config.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8000
  log_level: "info"

model:
  path: "models/your-model.gguf"
  context_size: 4096
  n_threads: 8
  n_gpu_layers: -1
  use_mmap: true
  use_mlock: false
```

### Tuning Notes

- `n_threads` → Physical CPU cores - 1
- `n_gpu_layers` → Adjust based on available VRAM
- `context_size` → Higher values increase memory usage

---

## Running the Server

```bash
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Wait for:

```
Application startup complete.
```

---

## API Reference

### Health Check

```
GET /health
```

```bash
curl http://localhost:8000/health
```

---

### Chat Completions (Streaming)

```
POST /v1/chat/completions
```

Example request:

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "List 3 colors."}
    ],
    "stream": true,
    "temperature": 0.7
  }'
```

Response is streamed as `text/event-stream`.

---

## Performance Characteristics

Performance depends on:

- Model size
- Quantization level
- GPU VRAM
- CPU core count
- Context size

Designed for:

- Single-model execution
- Deterministic request ordering
- Stable local multi-client usage

Not designed for:

- Horizontal scaling
- Distributed inference
- Public internet exposure
- Multi-model hot swapping

---

## Limitations

- Single global model instance
- Serialized inference (no parallel token generation)
- No authentication layer
- No rate limiting
- No TLS termination

Intended for trusted local environments.

---

## What This Project Demonstrates

- Backend system design
- Concurrency control in async environments
- Lifecycle-aware application startup
- Streaming API implementation
- Strict configuration validation
- Hardware-aware optimization

---

## Project Status

- Feature complete
- Stable for local inference
- No active feature development planned

This is a completed system design project focused on backend architecture and inference serving patterns.
