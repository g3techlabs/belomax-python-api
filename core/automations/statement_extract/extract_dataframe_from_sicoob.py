import pdfplumber
import pandas as pd

def extract_table_from_pdf(pdf_path):
	"""
	Extrai os dados tabulares de um PDF (se houver tabelas).
	Retorna um DataFrame contendo Data, Histórico e Valor.
	"""
	extracted_data = []
	with pdfplumber.open(pdf_path) as pdf:
		for page in pdf.pages:
			# Tenta extrair tabelas da página
			tables = page.extract_tables()
			for table in tables:
				for row in table:
					# Ajuste baseado no formato do Banco do Brasil (3 colunas)
					if len(row) == 3:
						extracted_data.append(row)
	# Converter para DataFrame
	df = pd.DataFrame(extracted_data, columns=["Data", "Historico", "Valor"])
	return df