import os
import redis
import json
import time
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def redis_consumer(redis_queue_name: str, job_handler: callable):
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", 6379))
    
    redis_client = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        decode_responses=True
    )

    queue_name = f"bull:{redis_queue_name}:wait"

    print(f"🚀 {datetime.now()} | Consumidor iniciado para a fila '{redis_queue_name}' ({queue_name})")
    
    while True:
        try:
            job_id = redis_client.lpop(queue_name)

            if job_id:
                job_key = f"bull:{redis_queue_name}:{job_id}"
                job_data = redis_client.hgetall(job_key)

                if not job_data:
                    print(f"⚠️ {datetime.now()} | Job ID {job_id} não encontrado na chave '{job_key}'")
                    continue

                print(f"🎯 {datetime.now()} | Job encontrado: {job_data}")

                job_name = job_data.get("name", "unknown")
                raw_data = job_data.get("data", "{}")

                try:
                    job_payload = json.loads(raw_data)
                except json.JSONDecodeError:
                    print(f"❌ {datetime.now()} | Erro ao decodificar payload do job {job_id}")
                    continue

                try:
                    job_handler(job_name, job_payload)
                except Exception as handler_error:
                    print(f"🔥 {datetime.now()} | Erro ao processar job '{job_name}'")
                    traceback.print_exc()
                
                # ✅ Job processado, opção de deletar:
                # redis_client.delete(job_key)
            else:
                time.sleep(1)
                print(f"🔄 {datetime.now()} | Nenhum job encontrado, aguardando...")

        except Exception as err:
            print(f"💥 {datetime.now()} | Erro inesperado no consumer loop")
            traceback.print_exc()
            time.sleep(5)
