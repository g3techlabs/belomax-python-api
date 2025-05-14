import os
import pandas as pd
import requests
from core.automations.pensioner_paycheck.scrape import scrape

API_BASE_URL = os.getenv("NEST_API_URL", "http://localhost:3000")

# Mapeamento de nomes de meses para números
MONTHS_MAP = {
  "janeiro": 1,
  "fevereiro": 2,
  "março": 3,
  "abril": 4,
  "maio": 5,
  "junho": 6,
  "julho": 7,
  "agosto": 8,
  "setembro": 9,
  "outubro": 10,
  "novembro": 11,
  "dezembro": 12
}

def month_str_to_int(month):
    if isinstance(month, int):
        return month
    if isinstance(month, str):
        return MONTHS_MAP.get(month.strip().lower(), 0)
    return 0

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
                "month": month_str_to_int(paycheck.get("month")),
                "year": int(paycheck.get("year")),
                "consignableMargin": float(paycheck.get("consignableMargin", 0)),
                "totalBenefits": float(paycheck.get("totalBenefits", 0)),
                "netToReceive": float(paycheck.get("netToReceive", 0)),
                "automationId": automation_id,
                "terms": []
            }

            for term in row.get("terms", []):
                dto_payload["terms"].append({
                    "month": month_str_to_int(term.get("month", "")),
                    "year": int(term.get("year", 0)),
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

        # update_status(automation_id, "FINISHED", auth_token)
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
