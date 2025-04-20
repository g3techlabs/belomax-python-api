from PyPDF2 import PdfReader
import pandas as pd
import re
import pdfplumber
import os

def extract_dataframe_from_bb(file_path: str) -> pd.DataFrame:
    print(f"📄 Extraindo dados do PDF: {file_path}")

    pdf = pdfplumber.open(file_path)
    transactions = []

    for index, page in enumerate(pdf.pages):
        # Crop da página para remover cabeçalho
        cropped = page.crop((0, 0.10 * float(page.height), page.width, page.height))
        extracted_data = cropped.extract_text()

        if not extracted_data:
            continue  # Página vazia ou ilegível

        lines = extracted_data.split("\n")

        i = 0
        while i < len(lines) - 1:
            line1 = lines[i].strip()
            line2 = lines[i + 1].strip()
            combined_line = f"{line1} {line2}"

            match_combined = re.match(
                r"(\d{2}/\d{2}/\d{4})\s+(.+?)\s+(\d{1,3}(?:\.\d{3})*,\d{2})\s*\((\+|-)\)",
                combined_line
            )

            if match_combined:
                date = match_combined.group(1)
                description = match_combined.group(2)
                amount = match_combined.group(3).replace(".", "").replace(",", ".")
                sign = match_combined.group(4)
                amount = float(amount) * (1 if sign == "+" else -1)

                transactions.append([date, description, amount, index + 1])
                i += 2
            else:
                i += 1

    if not transactions:
        print("⚠️ Nenhuma transação encontrada.")
        return pd.DataFrame(columns=["Data", "Historico", "Valor", "Pagina"])

    df = pd.DataFrame(transactions, columns=["Data", "Historico", "Valor", "Pagina"])
    df["Valor"] = df["Valor"].abs()
    df["Valor"] = df["Valor"].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    print("✅ Extração concluída com sucesso.")
    return df
