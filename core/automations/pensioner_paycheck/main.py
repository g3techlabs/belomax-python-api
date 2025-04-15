from core.automations.pensioner_paycheck.scrape import scrape_unique

def trigger_pensioner_paycheck(job_payload):
  print("Iniciando a automação de extração de contracheque de aposentados.")
  df = scrape_unique(job_payload)
  result = df.to_dict(orient="records")  # Convert DataFrame to a dictionary
  return result

