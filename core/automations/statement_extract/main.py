import os
from dotenv import load_dotenv
import pandas as pd
import requests
from core.automations.statement_extract.filter_dataframe import filter_df
from core.aws.download_s3_file import download_from_s3
from core.automations.statement_extract.extract_data import extract_data
from core.automations.statement_extract.fill_excel_template import fill_excel_template
import logging

logging.getLogger("pdfplumber").setLevel(logging.ERROR)

load_dotenv()
API_BASE_URL = os.getenv("NEST_API_URL", "http://localhost:3000")

def trigger_statement_extract(job_payload):
    print("🚀 Iniciando a automação de extração de termos de extratos bancários.")
    print(f"📦 Payload recebido: {job_payload}")

    automation_id = job_payload["automationId"]
    auth_token = job_payload["authToken"]

    try:
        local_path = download_from_s3(job_payload["fileAwsName"])
        print(f"📥 Arquivo baixado localmente em: {local_path}")

        result = extract_data(bank=job_payload["bank"], path=local_path)

        if not isinstance(result, pd.DataFrame):
            raise ValueError("extract_data não retornou um DataFrame válido.")

        print("🧾 Primeiras linhas do DataFrame extraído:")
        print(result.head())
        
        if "Data" in result.columns:
            # Cria uma nova coluna temporária só para ordenação
            try:
                # Caso venha como número (formato Excel), converte corretamente
                result["_DataTemp"] = pd.to_datetime(result["Data"], errors="coerce", origin='1899-12-30', unit='D')
            except Exception:
                # Caso venha como string no formato dd/mm/yyyy
                result["_DataTemp"] = pd.to_datetime(result["Data"], errors="coerce", dayfirst=True)

            result = result.sort_values(by="_DataTemp", ascending=True).drop(columns=["_DataTemp"])

            print("📅 DataFrame ordenado pela coluna 'Data' (desc):")
            print(result.head())
        else:
            raise KeyError("A coluna 'Data' não existe no DataFrame extraído.")

        if "Historico" not in result.columns:
            raise KeyError("A coluna 'Historico' não existe no DataFrame extraído.")

        terms = job_payload["terms"]
        filtered_result = []
        sheets_created = []
        terms_not_found = []
        
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

            # original_filename = os.path.basename(local_path).replace(".pdf", "")
            filename = f"filter-{term.replace(' ', '_')}-{job_payload["bank"].replace(' ', '_')}-{job_payload["customerName"].replace(' ', '_')}.xlsx"
            output_path = os.path.join("core/tmp", filename)

            # filtered_df.to_excel(output_path, index=False)
            # print(f"📄 Planilha criada: {output_path}")
            fill_excel_template(filtered_df, output_path, job_payload["customerName"])
            print(f"📊 Planilha preenchida: {output_path}")

            upload_success = upload_document(output_path, f"PLANILHA-{term.replace(' ', '_')}-{job_payload["bank"].replace(' ', '_')}-{job_payload["customerName"].replace(' ', '_')}", automation_id, auth_token)

            if upload_success:
                sheets_created.append(filename)
            else:
                print(f"❌ Falha ao enviar: {filename}")

            os.remove(output_path)
            filtered_result.append(filtered_df)

        if os.path.exists(local_path):
            os.remove(local_path)
            print(f"🗑️ Arquivo local removido: {local_path}")

        if len(sheets_created) == 0:
            print("⚠️ Nenhum termo encontrado. Nada foi salvo.")
            update_status(automation_id, "FAILED", auth_token, "Nenhum termo encontrado.")
        else:
            print(f"✅ Termos processados com sucesso: {len(sheets_created)}")
            # update_status(automation_id, "FINISHED", auth_token)

        print("✅ Automação de extração concluída.")
        return filtered_result

    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        update_status(automation_id, "FAILED", auth_token, str(e))

        if 'local_path' in locals() and os.path.exists(local_path):
            os.remove(local_path)
            print(f"🗑️ Arquivo local removido após erro: {local_path}")

        return []

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


def update_status(automation_id: str, status: str, token: str, error: str = None) -> None:
    url = f"{API_BASE_URL}/api/automations/{automation_id}/status"
    headers = {
        "Authorization": token
    }
    
    data = {
        "status": status
    }

    if error:
        data["error"] = error

    try:
        response = requests.put(url, json=data, headers=headers)
        if response.ok:
            print(f"✅ Status da automação atualizado para: {status}")
        else:
            print(f"❌ Falha ao atualizar status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exceção ao atualizar status da automação: {e}")
