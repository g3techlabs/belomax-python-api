import os
from dotenv import load_dotenv
import pandas as pd
import requests
from core.automations.statement_extract.filter_dataframe import filter_df
from core.aws.download_s3_file import download_from_s3
from core.automations.statement_extract.extract_data import extract_data
import logging

logging.getLogger("pdfplumber").setLevel(logging.ERROR)

load_dotenv()
API_BASE_URL = os.getenv("NEST_API_URL", "http://localhost:3000")

def trigger_statement_extract(job_payload):
    print("🚀 Iniciando a automação de extração de termos de extratos bancários.")
    print(f"📦 Payload recebido: {job_payload}")

    local_path = download_from_s3(job_payload["fileAwsName"])
    automation_id = job_payload["automationId"]
    auth_token = job_payload["authToken"]
    print(f"📥 Arquivo baixado localmente em: {local_path}")

    result = extract_data(bank=job_payload["bank"], path=local_path)

    if not isinstance(result, pd.DataFrame):
        print("❌ ERRO: extract_data não retornou um DataFrame válido!")
        os.remove(local_path)
        return []

    print("🧾 Primeiras linhas do DataFrame extraído:")
    print(result.head())

    if "Historico" not in result.columns:
        print("❌ A coluna 'Historico' não existe no DataFrame.")
        os.remove(local_path)
        return []

    terms = job_payload["terms"]
    filtered_result = []
    terms_not_found = []
    sheets_created = []

    for term in terms:
        print(f"🔍 Buscando termo no histórico: '{term}'")
        filtered_df = filter_df(result, "Historico", term)

        if filtered_df.empty:
            print(f"⚠️ Nenhuma correspondência encontrada para o termo: '{term}'")
            terms_not_found.append(term)
            continue
        else:
            print(f"✅ Termo encontrado. Linhas retornadas: {len(filtered_df)}")
            print(filtered_df)
            
        # timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        original_filename = os.path.basename(local_path).replace(".pdf", "")
        filename = f"{original_filename}-filter-{term.replace(' ', '_')}.xlsx"
        output_path = os.path.join("core/tmp", filename)

        filtered_df.to_excel(output_path, index=False)
        print(f"📄 Planilha criada: {output_path}")

        # Enviar para Nest
        upload_success = upload_document(output_path, filename, automation_id, auth_token)

        if upload_success:
            sheets_created.append(filename)
        else:
            print(f"❌ Falha ao enviar: {filename}")

        os.remove(output_path)

        filtered_result.append(filtered_df)

    # Remover o arquivo local temporário
    if os.path.exists(local_path):
        os.remove(local_path)
        print(f"🗑️ Arquivo local removido: {local_path}")
        
    if len(sheets_created) == 0:
        print("⚠️ Nenhum termo encontrado. Nada foi salvo.")
        update_status(automation_id, "FAILED", auth_token)
    else:
        print(f"✅ Termos processados com sucesso: {len(sheets_created)}")
        update_status(automation_id, "FINISHED", auth_token)

    print("✅ Automação de extração concluída.")
    return filtered_result

def upload_document(path: str, name: str, automation_id: str, token: str) -> bool:
    url = f"{API_BASE_URL}/api/documents"
    headers = {
        "Authorization": token
    }

    try:
        with open(path, 'rb') as file_data:
            files = {'file': file_data}
            data = {'name': name, 'automationId': automation_id}
            response = requests.post(url, headers=headers, files=files, data=data)
        if response.status_code == 201:
            print(f"✅ Upload bem-sucedido: {name}")
            return True
        else:
            print(f"❌ Erro ao fazer upload: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exceção ao enviar documento: {e}")
        return False


def update_status(automation_id: str, status: str, token: str) -> None:
    url = f"{API_BASE_URL}/api/automations/{automation_id}/status"
    headers = {
        "Authorization": token
    }

    try:
        response = requests.put(url, json={'status': status}, headers=headers)
        if response.ok:
            print(f"✅ Status da automação atualizado para: {status}")
        else:
            print(f"❌ Falha ao atualizar status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exceção ao atualizar status da automação: {e}")