import os
import redis
import json
import time

# ! ATENÇÃO: SE O PROCESSOR DO NESTJS ESTIVER ATIVADO, ELE INTERCEPTA OS JOBS, E O PYTHON NÃO CONSEGUE LER

def redis_consumer(redis_queue_name):
  print(os.getenv("REDIS_HOST"), os.getenv("REDIS_PORT"))
  # Conectar ao Redis
  redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, decode_responses=True)

  queue_name = f"bull:{redis_queue_name}:wait"
  
  print(f"🚀 Consumidor iniciado para a fila '{redis_queue_name}'")

  while True:
    # Pega um job da fila (FIFO - primeiro que entra, primeiro que sai)
    job_id = redis_client.lpop(queue_name)

    if job_id:
        # Buscar detalhes do job
      job_key = f"bull:users-queue:{job_id}"
      job_data = redis_client.hgetall(job_key)

      if job_data:
        print(f"🎯 Job encontrado: {job_data}")

        # Decodificar os dados
        job_name = job_data.get("name", "unknown")
        job_payload = json.loads(job_data.get("data", "{}"))  # Convertendo JSON para dicionário

        if job_name == "send-credentials-email":
          email = job_payload.get("email")
          password = job_payload.get("password")
          print(f"📧 Enviando e-mail para {email} com a senha {password}")

          # 🔥 Se quiser remover o job do Redis após processá-lo
          redis_client.delete(job_key)

    else:
      time.sleep(1)
      print("🔄 Nenhum job encontrado, aguardando...")

# 🎯 Job encontrado: {'name': 'send-credentials-email', 'data': '{"email":"gabrielguilherme13@hotmail.com","password":"teste123"}', 'opts': '{"attempts":0}', 'timestamp': '1743551961137', 'delay': '0', 'priority': '0'}
# 📧 Enviando e-mail para gabrielguilherme13@hotmail.com com a senha teste123