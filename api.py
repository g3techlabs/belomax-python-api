# main.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from dotenv import load_dotenv
import uvicorn
import os

from core.automations.statement_extract.extract_data import extract_data
from core.automations.statement_extract.extract_dataframe_from_bb import extract_dataframe_from_bb
from core.automations.statement_extract.extract_dataframe_from_bradesco import extract_dataframe_from_bradesco
from core.automations.statement_extract.extract_dataframe_from_sicoob import extract_table_from_pdf
from core.utils.terms import extract_unique_terms

from core.redis_queue.consumer import redis_consumer
from multiprocessing import Process

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/extract-terms")
async def extract_terms(file: UploadFile, bank: str = Form(...)) -> List[str]:
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    match bank.upper():
        case "BB":
            df = extract_dataframe_from_bb(temp_path)
        case "BRADESCO":
            df = extract_dataframe_from_bradesco(temp_path)
        case "SICOOB":
            df = extract_table_from_pdf(temp_path)
        case _:
            return []

    os.remove(temp_path)
    return extract_unique_terms(df)
