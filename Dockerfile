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

# Baixe e instale o Chrome for Testing
RUN wget -O /tmp/chrome-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/137.0.7151.0/linux64/chrome-linux64.zip && \
    unzip /tmp/chrome-linux64.zip -d /opt/ && \
    ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome && \
    rm /tmp/chrome-linux64.zip

# Baixe e instale o ChromeDriver correspondente
RUN wget -O /tmp/chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/137.0.7151.0/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver-linux64.zip -d /opt/ && \
    ln -s /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    rm /tmp/chromedriver-linux64.zip

# 5️⃣ Expõe a porta da API (FastAPI)
EXPOSE 8000
RUN chmod +x /usr/bin/chromedriver

# 6️⃣ Comando padrão (sobrescrito no docker-compose)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]