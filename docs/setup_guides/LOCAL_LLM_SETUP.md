# Local LLM Setup

Install Ollama, then run:

```bash
ollama pull llama3.1:8b
ollama serve
```

Set `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
USE_PAID_API=false
```

OpenWebUI can be used through an OpenAI-compatible endpoint by setting `LLM_PROVIDER=openwebui` and `OPENWEBUI_BASE_URL`.

