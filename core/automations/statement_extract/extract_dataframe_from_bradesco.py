import re
from PyPDF2 import PdfReader
import pandas as pd
from datetime import datetime
import os

def pdf_to_txt(pdf_path: str, txt_path: str) -> None:
    """Transforma o conteúdo de um PDF em um arquivo TXT."""
    reader = PdfReader(pdf_path)
    with open(txt_path, 'w', encoding='utf-8') as f:
        for page in reader.pages:
            f.write(page.extract_text())
    return

def read_file(txt_path: str) -> list[str]:
    """Lê o arquivo TXT e retorna uma lista de linhas sem espaços desnecessários."""
    with open(txt_path, 'r', encoding='utf-8') as file:
        lines = [line.strip() for line in file if line.strip()]
    return lines

def clean_line(line: str) -> str:
    """Remove palavras irrelevantes ou elementos que não fazem parte das transações."""
    unwanted = ['Saldo', '(R$)', 'Crédito', 'Débito', 'Docto.', 'Histórico', 'Data']
    for word in unwanted:
        line = line.replace(word, '')
    return line.strip()

def extract_date(line: str) -> None | str:
    """Extrai a data de uma linha do extrato, mesmo que esteja colada a texto."""
    # Regex ajustado para capturar datas mesmo se coladas com texto
    pattern = r'\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/\d{4}(?=\D|$)'
    match = re.search(pattern, line)
    return match.group(0) if match else None

def extract_value(line: str) -> list[str]:
    """Extrai todos os valores monetários de uma linha do extrato."""
    pattern = r'\b\d{1,3}(?:\.\d{3})*,\d{2}\b'
    return re.findall(pattern, line)
  
def find_next_date(lines: list[str], index: int, first_date: str) -> None | str:
    """Encontra a próxima data válida no extrato."""
    for i in range(index, len(lines)):
        if i >= len(lines) - 1:
            return None
    
        if (detect_header_line(lines[i])):
            continue
        
        date = extract_date(lines[i])
        if date and date != first_date:
            return { "date": date, "index": i+1 }
    return None
  
def detect_header_line(line: str) -> bool:
    """Ignora as linhas iniciais do extrato que não contêm transações."""
    pattern = r'^Bradesco Celular|\b\d{2}h\d{2}\b|^Nome:|^Extrato de:|\b\d{2}/\d{2}/\d{4}\b.*\b\d{2}/\d{2}/\d{4}\b|\bFolha:\b'
    detected_line = re.search(pattern, line)
    return detected_line

def extract_dataframe_from_bradesco(pdf_path: str) -> pd.DataFrame:
    """Converte o extrato PDF para um DataFrame com colunas 'Data', 'Histórico' e 'Valor'."""
    # Converte PDF para TXT
    tmp_dir = "core/tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_path = os.path.join(tmp_dir, f"extrato_bradesco_{timestamp}.txt")

    # Converte PDF para TXT
    pdf_to_txt(pdf_path, txt_path)

    # Lê o TXT
    lines = read_file(txt_path)

    # Inicializa o DataFrame
    df = pd.DataFrame(columns=["Data", "Historico", "Valor", "Pagina"])
    first_date = None
    next_date = { "date": None, "index": 0 }
    last_date = None
    current_page = 0
    
    for index, line in enumerate(lines):
      line = clean_line(line)
      
      date = extract_date(line)
      
      if date:
        first_date = date
        break

    for index, line in enumerate(lines):
        line = clean_line(line)
        
        if "Folha:" in line:
          # current_page = line[len(line) - 3]
          current_page = line.split(" ")[-1].split("/")[0].strip()
          
        if detect_header_line(line):
          continue
          
        # if index - 1 != len(lines) and index >= next_date["index"] or not next_date["date"]:
        #   found_next_date = find_next_date(lines, next_date["index"], first_date)
        #   if found_next_date:
        #     next_date = found_next_date
            
        # date = extract_date(line) or next_date["date"]
        
        date = extract_date(line)
        values = extract_value(line)
        history = line
        if date and date != first_date:
            last_date = date
            history = history.replace(date, '').strip()
        else:
            date = last_date
        for value in values:
            history = history.replace(value, '').strip()

        # Adiciona a linha ao DataFrame
        row = {
            "Data": date,
            "Historico": " ".join(re.findall(r'[A-Za-zÀ-ÿ0-9\.\-\*/\(\)\&]+', history)),
            "Valor": values[0] if len(values) > 0 else '',
            "Pagina": current_page
        }
        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

    # Preenche valores ausentes em 'Valor'
    for i in range(len(df) - 1):
        if df.loc[i, 'Valor'] == '':
            df.loc[i, 'Valor'] = df.loc[i + 1, 'Valor']

    # Preenche datas ausentes em 'Data'
    last_date = None
    for i in range(len(df)):
        if pd.notna(df.loc[i, 'Data']):
            last_date = df.loc[i, 'Data']
        else:
            df.loc[i, 'Data'] = last_date

    if os.path.exists(txt_path):
        os.remove(txt_path)

    return df
