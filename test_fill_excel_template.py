import pandas as pd
from core.automations.statement_extract.fill_excel_template import fill_excel_template
from core.automations.statement_extract.extract_dataframe_from_bradesco import extract_dataframe_from_bradesco
from core.automations.statement_extract.filter_dataframe import filter_df

def test_fill_excel_template():
    # Caminho do PDF de entrada
    pdf_path = './extratobradesco.pdf'

    # Extrai o DataFrame do PDF
    df = extract_dataframe_from_bradesco(pdf_path)

    # Caminho do template e saída
    output_path = './core/templates/Extrato_Preenchido_Com_Estilo.xlsx'
    nome = 'THIAGO'
    
    filtered_df = filter_df(df, "Historico", "resgate")

    # Testa a função
    fill_excel_template(filtered_df, output_path, nome)
    print(f"Arquivo gerado com sucesso: {output_path}")

if __name__ == "__main__":
    test_fill_excel_template()
