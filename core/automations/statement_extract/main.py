# core/automations/statement_extract/main.py

from core.aws.download_s3_file import extract_from_s3
from core.automations.statement_extract.extract_data import extract_data

def trigger_statement_extract(job_payload):
    print("Iniciando a automação de extração de termos de extratos bancários.")
    print(job_payload)
    local_path = extract_from_s3(job_payload["fileAwsName"])
    print(f"📥 Arquivo baixado localmente em: {local_path}")
    # result = extract_data(job_payload)
    # return result