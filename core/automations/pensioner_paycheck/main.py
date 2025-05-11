import os
import pandas as pd
import requests
from core.automations.pensioner_paycheck.scrape import scrape

API_BASE_URL = os.getenv("NEST_API_URL", "http://localhost:3000")

def trigger_pensioner_paycheck(job_payload):
    print("🚀 Iniciando a automação de extração de contracheque de aposentados.")
    print(f"📦 Payload recebido: {job_payload}")

    automation_id = job_payload.get("automationId")
    auth_token = job_payload.get("authToken")
    data_items = job_payload.get("data", [])

    try:
        df = pd.DataFrame(data_items)
        df = df.rename(columns={
            "registration": "matricula",
            "bond": "vinculo",
            "cpf": "cpf",
            "pensionerNumber": "numpens",
            "month": "mes",
            "year": "ano"
        })
        result_data = scrape(df)
        
        if not result_data:
            raise ValueError("A lista retornada pela função scrape está vazia.")

        for row in result_data:
            paycheck = row.get("paycheck", {})
            dto_payload = {
                "registration": paycheck.get("registration"),
                "bond": paycheck.get("bond"),
                "cpf": paycheck.get("cpf"),
                "pensionerNumber": paycheck.get("pensionerNumber"),
                "month": paycheck.get("month"),
                "year": paycheck.get("year"),
                "consignableMargin": float(paycheck.get("consignableMargin", 0)),
                "totalBenefits": float(paycheck.get("totalBenefits", 0)),
                "netToReceive": float(paycheck.get("netToReceive", 0)),
                "automationId": automation_id,
                "terms": []
            }

            # Convertendo os termos
            for term in row.get("terms", []):
              dto_payload["terms"].append({
                  "month": str(term.get("month", "")),
                  "year": str(term.get("year", "")),
                  "type": str(term.get("type", "")),
                  "code": int(term.get("code", 0)),
                  "discrimination": str(term.get("discrimination", "")),
                  "value": float(term.get("value", 0))
              })

            headers = {
                "Authorization": auth_token,
                "Content-Type": "application/json"
            }

            url = f"{API_BASE_URL}/api/pensioner-paychecks"
            response = requests.post(url, json=dto_payload, headers=headers)

            if response.status_code == 201:
                print(f"✅ Contracheque enviado com sucesso: {dto_payload['cpf']} - {dto_payload['month']}/{dto_payload['year']}")
            else:
                raise Exception(f"Falha ao enviar dados: {response.status_code} - {response.text}")

        update_status(automation_id, "FINISHED", auth_token)
        print("✅ Automação finalizada com sucesso.")

    except Exception as e:
        print(f"❌ Erro na automação de contracheques: {e}")
        update_status(automation_id, "FAILED", auth_token, str(e))

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