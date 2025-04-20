from core.automations.statement_extract.extract_dataframe_from_sicoob import extract_table_from_pdf
from core.automations.statement_extract.extract_dataframe_from_bradesco import extract_dataframe_from_bradesco
from core.automations.statement_extract.extract_dataframe_from_bb import extract_dataframe_from_bb

def extract_data(path, bank):
  """
  Handles the extraction of bank statements based on the selected bank.
  :param data: Dictionary containing 'selected_bank' and 'input_pdf_path' (S3 link).
  :return: Extracted data as a DataFrame or error message.
  """
  df = None

  match bank:
    case "BRADESCO":
      df = extract_dataframe_from_bradesco(path)
    case "BB":
      df = extract_dataframe_from_bb(path)
    case "SICOOB":
      df = extract_table_from_pdf(path)
    case "CAIXA":
      print("Em desenvolvimento")
    case _:
      print("Banco não reconhecido")
      return "Erro: Banco não reconhecido."
  
  return df

