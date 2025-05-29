# ───────────────────────────────────────
#  Imagem base com Chrome + Selenium
# ───────────────────────────────────────
FROM selenium/standalone-chrome:latest

# ───────────────────────────────────────
#  Instala Python, pip e compiladores
# ───────────────────────────────────────
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        libffi-dev && \
    pip3 install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# ───────────────────────────────────────
#  Configura o diretório da aplicação
# ───────────────────────────────────────
WORKDIR /app

# Copia o requirements antes para aproveitamento de cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o restante do código
COPY . .

# Ajusta permissões para o usuário não-root da imagem Selenium
RUN chown -R seluser:seluser /app
USER seluser

# ───────────────────────────────────────
#  Definições de ambiente e porta
# ───────────────────────────────────────
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

EXPOSE ${PORT}

# ───────────────────────────────────────
#  Comando de inicialização (ajuste se necessário)
# ───────────────────────────────────────
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]