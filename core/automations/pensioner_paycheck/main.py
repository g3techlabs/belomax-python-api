<<<<<<< Updated upstream
from pensioner_paycheck.scrape import scrape
from utils.excel import read_excel, write_excel, write_not_found_excel_clone

def trigger_pensioner_paycheck():
  print("Iniciando a automação de extração de contracheque de aposentados.")
  
  df = read_excel(all_excel[i])
  scraped_data = scrape(df, all_excel[i])
  excel_done = write_excel(scraped_data[0], all_excel[i])
  print(f"Você pode encontrá-la em '{excel_done}'\n")
  
  excel_not_done = write_not_found_excel_clone(scraped_data[1], all_excel[i])
  
  if excel_not_done.strip() != '':
    print(f"Para os casos não encontrados, você pode encontrá-los em '{excel_not_done}'")
=======
from core.automations.pensioner_paycheck.scrape import scrape_unique

def trigger_pensioner_paycheck(job_payload):
  print("Iniciando a automação de extração de contracheque de aposentados.")
  df = scrape_unique(job_payload)
  result = df.to_dict(orient="records")  # Convert DataFrame to a dictionary
  return result

>>>>>>> Stashed changes
