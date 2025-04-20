import os
import pandas as pd
from core.automations.statement_extract.filter_dataframe import filter_df
from core.aws.download_s3_file import extract_from_s3
from core.automations.statement_extract.extract_data import extract_data

def trigger_statement_extract(job_payload):
    print("🚀 Iniciando a automação de extração de termos de extratos bancários.")
    print(f"📦 Payload recebido: {job_payload}")

    local_path = extract_from_s3(job_payload["fileAwsName"])
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

    for term in terms:
        print(f"🔍 Buscando termo no histórico: '{term}'")
        filtered_df = filter_df(result, "Historico", term)

        if filtered_df.empty:
            print(f"⚠️ Nenhuma correspondência encontrada para o termo: '{term}'")
        else:
            print(f"✅ Termo encontrado. Linhas retornadas: {len(filtered_df)}")
            print(filtered_df)

        filtered_result.append(filtered_df)

    # Remover o arquivo local temporário
    if os.path.exists(local_path):
        os.remove(local_path)
        print(f"🗑️ Arquivo local removido: {local_path}")

    print("✅ Automação de extração concluída.")
    return filtered_result
