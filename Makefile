.PHONY: help api worker all

# Caminhos
PYTHON=python
FASTAPI_PORT=8000

help:
	@echo ""
	@echo "📚 Comandos disponíveis:"
	@echo "  make api       -> Inicia a FastAPI na porta $(FASTAPI_PORT)"
	@echo "  make worker    -> Inicia o worker da fila Redis"
	@echo "  make all       -> Inicia API e worker em paralelo"

api:
	@echo "🚀 Iniciando FastAPI..."
	@uvicorn api:app --host 0.0.0.0 --port $(FASTAPI_PORT) --reload


worker:
	@echo "🧠 Iniciando Redis Worker..."
	@$(PYTHON) main.py

all:
	@echo "🔥 Iniciando API e Worker em paralelo..."
	@$(MAKE) -j2 api worker
