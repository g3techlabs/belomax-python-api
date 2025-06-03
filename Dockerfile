# ───────────────────────────────────────
#  Imagem base com Chrome + Selenium
# ───────────────────────────────────────
FROM selenium/standalone-chrome:latest

# ───────────────────────────────────────
#  Instala Python, pip e compiladores
# ───────────────────────────────────────
USER root
# Atualiza apenas o pip já existente na imagem, evitando dependências de sistema
RUN python3 -m pip install --upgrade pip

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
    PORT=8000 \
    PYTHONPATH=/app \
    SELENIUM_ENV="remote"

EXPOSE ${PORT}

# ───────────────────────────────────────
#  Comando de inicialização (ajuste se necessário)
# ───────────────────────────────────────
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]