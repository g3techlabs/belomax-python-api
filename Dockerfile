# Usa a imagem oficial do Selenium com Chrome
FROM selenium/standalone-chrome:latest

# Define o usuário como root para instalar pacotes adicionais
USER root

# Atualiza o sistema e instala o Python 3.12
RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update && \
  apt-get install -y python3.12 python3.12-distutils && \
  ln -s /usr/bin/python3.12 /usr/bin/python3 && \
  rm -rf /var/lib/apt/lists/*

# Instala o pip para o Python 3.12
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o contêiner
COPY . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta da API (se aplicável)
EXPOSE 8000

# Comando padrão para iniciar a aplicação (ajuste conforme necessário)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]