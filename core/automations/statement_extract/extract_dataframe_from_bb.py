from PyPDF2 import PdfReader
import pandas as pd
import re
import pdfplumber
import os

def extract_dataframe_from_bb(file_path: str) -> pd.DataFrame:
    """
    Extrai transações específicas de um PDF do BB no formato:
    - Linha 1: Data + Descrição ou apenas Data.
    - Linha 2: Descrição + Valor ou apenas Valor.
    """
    pdf = pdfplumber.open(file_path)
    transactions = []
    
    for index, page in enumerate(pdf.pages):
        # Remover cabeçalhos usando crop
        cropped = page.crop((0, 0.10 * float(page.height), page.width, page.height))
        extracted_data = cropped.extract_text()

        # Separar o texto em linhas
        lines = extracted_data.split("\n")
        
        # Processar as linhas
        i = 0
        while i < len(lines) - 1:  # Percorre até a penúltima linha
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()

            # Combina as duas linhas em uma única análise
            combined_line = f"{line1} {line2}"

            # Regex para capturar Data, Descrição e Valor
            match_combined = re.match(
                r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s*\((\+|-)\)", 
                combined_line
            )

            if match_combined:
                # Extração dos dados
                date = match_combined.group(1)
                description = match_combined.group(2)
                amount = match_combined.group(3).replace(".", "").replace(",", ".")
                amount_type = match_combined.group(4)
                amount = float(amount) * (1 if amount_type == "+" else -1)

                # Adiciona ao array de transações
                transactions.append([date, description, amount, index + 1])

                # Pula as duas linhas
                i += 2
            else:
                i += 1  # Continua para a próxima linha

    # Cria o DataFrame com os dados capturados
    df = pd.DataFrame(transactions, columns=["Data", "Historico", "Valor", "Pagina"])
    df["Valor"] = df["Valor"].abs()
    df["Valor"] = df["Valor"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # Salva o DataFrame em Excel
    return df
