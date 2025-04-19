# core/aws/download_s3_file.py

import boto3
import os
import logging
import json
import time
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Carrega variáveis do .env
load_dotenv()

def download_from_s3(key):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    # Variáveis de ambiente
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    region = os.getenv("AWS_REGION")
    bucket = os.getenv("AWS_S3_BUCKET")

    # Caminho do diretório 'tmp' dentro do projeto
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # vai até /core
    tmp_dir = os.path.join(base_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    # Caminho completo do arquivo
    local_path = os.path.join(tmp_dir, os.path.basename(key))

    # Inicializa o S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=region
    )

    # Tenta baixar o arquivo
    max_tries = 10
    attempt = 1
    while attempt <= max_tries:
        logging.info(f"🔄 Tentativa {attempt}/{max_tries} para verificar existência de '{key}' no bucket '{bucket}'")
        try:
            response = s3.head_object(Bucket=bucket, Key=key)
            logging.info("📦 Arquivo encontrado no S3!")
            break
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                logging.info("⏳ Arquivo ainda não disponível. Aguardando...")
            else:
                logging.error(f"❌ Erro ao verificar arquivo: {e}")
            time.sleep(1)
            attempt += 1
    else:
        raise Exception(f"⚠️ Arquivo '{key}' não encontrado após {max_tries} tentativas.")

    try:
        s3.download_file(bucket, key, local_path)
        logging.info(f"✅ Download completo: {local_path}")
    except Exception as e:
        logging.error(f"❌ Erro ao baixar o arquivo: {e}")
        raise

    return local_path

def extract_from_s3(key):
    """Baixa o PDF do S3 e retorna o caminho local."""
    return download_from_s3(key)
