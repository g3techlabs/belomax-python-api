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

# Instala dependências necessárias
RUN apt-get update && apt-get install -y \
  wget \
  unzip \
  gnupg \
  curl \
  ca-certificates \
  fonts-liberation \
  libappindicator3-1 \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libcups2 \
  libdbus-1-3 \
  libgdk-pixbuf2.0-0 \
  libnspr4 \
  libnss3 \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  xdg-utils \
  --no-install-recommends && \
  rm -rf /var/lib/apt/lists/*

# Adiciona a chave e o repositório do Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
  echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Instala o Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable && \
  rm -rf /var/lib/apt/lists/*

# Baixa e instala o ChromeDriver compatível
RUN CHROME_VERSION=$(google-chrome-stable --version | grep -oP '\d+\.\d+\.\d+') && \
  CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d '.' -f 1) && \
  CHROMEDRIVER_VERSION=$(curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_MAJOR_VERSION") && \
  wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" && \
  unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
  rm /tmp/chromedriver.zip && \
  chmod +x /usr/local/bin/chromedriver

# 5️⃣ Expõe a porta da API (FastAPI)
EXPOSE 8000

# 6️⃣ Comando padrão (sobrescrito no docker-compose)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]