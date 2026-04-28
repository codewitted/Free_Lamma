#!/usr/bin/env bash
set -euo pipefail
echo "Install Ollama from https://ollama.com, then run:"
echo "  ollama pull llama3.1:8b"
echo "  ollama serve"
echo "Optional OpenWebUI:"
echo "  docker run -p 3000:8080 -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main"

