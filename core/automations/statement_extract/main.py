from core.automations.statement_extract.extract_data import extract_data

def trigger_statement_extract(job_payload):
    print("Iniciando a automação de extração de termos de extratos bancários.")
    result = extract_data(job_payload)
    print("Resultado da extração:", result)

