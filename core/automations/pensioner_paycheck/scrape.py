# Refatoração da função `scrape` para retornar dados no formato do modelo `PensionerPaycheck` e `PensionerPaycheckTerm`

import os
from typing import List, Dict, Union
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as SeleniumTimeoutException
from time import time, sleep
import pandas as pd
import numpy as np
from core.utils.functions import convert_month, convert_seconds_to_formatted_time

def scrape(df: pd.DataFrame) -> List[Dict[str, Union[dict, list]]]:
    print(f"Iniciando extração dos Contracheques de Pensionistas\n")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # driver: WebDriver = webdriver.Chrome(options=options)

    # selenium_server_url = "http://localhost:4444/wd/hub"

    # Leia a variável de ambiente. Se não estiver definida, assume 'local'.
    selenium_remote_url = os.getenv("SELENIUM_REMOTE_URL", "local")

    if selenium_remote_url != "local":
        print("Usando WebDriver Remoto (Produção/Docker).")
        # Conecta-se ao servidor Selenium que está rodando no container (fornecido pela imagem base)
        driver: WebDriver = webdriver.Remote(
            command_executor=selenium_remote_url, # Ou 'http://127.0.0.1:4444/wd/hub'
            options=options
        )
    else:
        print("Usando WebDriver Chrome Local (Desenvolvimento).")
        # Para desenvolvimento local.
        # O Selenium 4+ tenta gerenciar o chromedriver automaticamente (Selenium Manager).
        # Se você tiver problemas, pode precisar especificar o caminho para o chromedriver
        # usando webdriver.ChromeService:
        # from selenium.webdriver.chrome.service import Service as ChromeService
        # service = ChromeService(executable_path='/caminho/para/seu/chromedriver')
        # driver: WebDriver = webdriver.Chrome(service=service, options=options)
        driver: WebDriver = webdriver.Chrome(options=options)

    initial_time = time()
    resultados = []

    for i in range(len(df)):
        driver.get('http://servicos.searh.rn.gov.br/searh/copag/contra_cheque_pensionistas.asp')
        try:
            # Preenchimento do formulário
            driver.find_element(By.ID, 'matricula').send_keys(str(df['matricula'][i]))
            driver.find_element(By.ID, 'vinculo').send_keys(str(df['vinculo'][i]))
            driver.find_element(By.ID, 'cpf').send_keys(str(df['cpf'][i]))
            driver.find_element(By.ID, 'numpens').send_keys(str(df['numpens'][i]))
            driver.find_element(By.ID, 'mes').click()
            driver.find_element(By.XPATH, f"/html/body/div[1]/div[2]/div/div/div[2]/form/div[5]/select/option[{convert_month(str.lower(df['mes'][i]))}]").click()
            driver.find_element(By.ID, 'ano').send_keys(str(df['ano'][i]))
            driver.find_element(By.ID, 'frmDados').submit()
            
            try:
              find_cpf_xpath = '/html/body/table[2]/tbody/tr[2]/td[3]/font[2]/font'
              
              print(f"INFO [{i+1}]: Formulário enviado. Aguardando elemento chave do contracheque ({find_cpf_xpath}) por até 60s...", flush=True)
              
              WebDriverWait(driver, 60).until( # Espere por até 60 segundos (ajuste conforme necessário)
                  EC.presence_of_element_located((By.XPATH, find_cpf_xpath))
              )
              
              print(f"INFO [{i+1}]: Elemento chave do contracheque encontrado. URL atual: {driver.current_url}", flush=True)
              
              if "contrachk" not in driver.current_url:
                  print(f"{i + 1}: Registro não encontrado para CPF: {df['cpf'][i]}")
                  continue

              # Extrair dados principais
              paycheck = {
                  "registration": driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr[1]/td[2]/font/font[2]').text,
                  "bond": driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr[1]/td[3]/font/font[2]').text,
                  "cpf": driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr[2]/td[3]/font[2]/font').text,
                  "pensionerNumber": driver.find_element(By.XPATH, '/html/body/table[2]/tbody/tr[1]/td[4]/font[2]/font').text,
                  "month": df['mes'][i],
                  "year": df['ano'][i],
                  "consignableMargin": float(driver.find_element(By.XPATH, '/html/body/table[4]/tbody/tr/td[1]/div/font/b/font[2]/font').text.replace("R$", "").replace(".", "").replace(",", ".").strip()),
                  "totalBenefits": float(driver.find_element(By.XPATH, '/html/body/table[4]/tbody/tr/td[2]/div/font/font[2]/b').text.replace("R$", "").replace(".", "").replace(",", ".").strip()),
                  "netToReceive": float(driver.find_element(By.XPATH, '/html/body/table[4]/tbody/tr/td[4]/p/font/font[2]/b').text.replace("R$", "").replace(".", "").replace(",", ".").strip())
              }
              
              # Extrair termos (vantagens e descontos)
              terms: List[Dict[str, Union[int, str, float]]] = []
              comp_disc_rows = driver.find_elements(By.XPATH, '/html/body/table[3]/tbody/tr')
              
              for j in range(1, len(comp_disc_rows) - 1):
                  codigo = int(driver.find_element(By.XPATH, f"/html/body/table[3]/tbody/tr[{j + 1}]/td[1]/font/b/font/font").text)
                  discriminacao = driver.find_element(By.XPATH, f"/html/body/table[3]/tbody/tr[{j + 1}]/td[2]/font/b/font/font").text

                  valor_van = driver.find_element(By.XPATH, f"/html/body/table[3]/tbody/tr[{j + 1}]/td[3]/font/b/font/font").text
                  if valor_van.strip() != "":
                      valor = float(valor_van.replace("R$", "").replace(".", "").replace(",", ".").strip())
                      terms.append({
                          "month": df["mes"][i],
                          "year": df["ano"][i],
                          "type": "BENEFIT",
                          "code": codigo,
                          "discrimination": discriminacao,
                          "value": valor,
                      })

                  valor_des = driver.find_element(By.XPATH, f"/html/body/table[3]/tbody/tr[{j + 1}]/td[4]/font/b/font/b/font/font").text
                  if valor_des.strip() != "":
                      valor = float(valor_des.replace("R$", "").replace(".", "").replace(",", ".").strip())
                      terms.append({
                          "month": df["mes"][i],
                          "year": df["ano"][i],
                          "type": "DISCOUNT",
                          "code": codigo,
                          "discrimination": discriminacao,
                          "value": valor,
                      })

              resultados.append({
                  "paycheck": paycheck,
                  "terms": terms
              })

              print(f"{i + 1}: Registro processado com sucesso para CPF: {df['cpf'][i]}")
            except SeleniumTimeoutException:
                print(f"ERRO [{i + 1}]: Timeout (60s) esperando pela página/elemento do contracheque para CPF: {df['cpf'][i]}.", flush=True)
                print(f"URL no momento do timeout: {driver.current_url}", flush=True)
                # Adicione aqui qualquer lógica de debug que você queira, como salvar o HTML
                # with open(f"debug_timeout_cpf_{df['cpf'][i]}.html", "w", encoding="utf-8") as f:
                #     f.write(driver.page_source)
                continue # Pula para o próximo item do DataFrame
        except Exception as e:
            print(f"Erro ao processar linha {i + 1}: {e}")

    print(f"\nExtração finalizada! Tempo total: {convert_seconds_to_formatted_time(time() - initial_time)}")
    driver.quit()
    return resultados