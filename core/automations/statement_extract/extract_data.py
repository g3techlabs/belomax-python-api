from core.automations.statement_extract.extract_dataframe_from_sicoob import extract_table_from_pdf
from core.automations.statement_extract.extract_dataframe_from_bradesco import extract_dataframe_from_bradesco
from core.automations.statement_extract.extract_dataframe_from_bb import extract_dataframe_from_bb

def extract_data(data):
    """
    Handles the extraction of bank statements based on the selected bank.
    :param data: Dictionary containing 'selected_bank' and 'input_pdf_path' (S3 link).
    :return: Extracted data as a DataFrame or error message.
    """
    df = None

    match data["selected_bank"]:
        case "Bradesco":
            df = extract_dataframe_from_bradesco(data["input_pdf_path"])
        case "Banco do Brasil":
            df = extract_dataframe_from_bb(data["input_pdf_path"])
        case "Sicoob":
            df = extract_table_from_pdf(data["input_pdf_path"])
        case _:
            print("Banco não reconhecido")
            return "Erro: Banco não reconhecido."
    
    return df.to_dict(orient="records") if df is not None else "Erro: Falha na extração."

