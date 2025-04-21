# Dockerfile

# 1️⃣ Usa uma imagem base oficial leve
FROM python:3.12-slim

# 2️⃣ Define diretório de trabalho dentro do container
WORKDIR /app

# 3️⃣ Copia arquivos necessários para dentro do container
COPY . .

# 4️⃣ Instala dependências
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 5️⃣ Expõe a porta da API (FastAPI)
EXPOSE 8000

# 6️⃣ Comando padrão (sobrescrito no docker-compose)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
