import redis
import json
import time

# ! ATENÇÃO: SE O PROCESSOR DO NESTJS ESTIVER ATIVADO, ELE INTERCEPTA OS JOBS, E O PYTHON NÃO CONSEGUE LER

# Conectar ao Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

queue_name = "bull:users-queue:wait"

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

      if job_name == "send_credentials_email_python":
        email = job_payload.get("email")
        password = job_payload.get("password")
        print(f"📧 Enviando e-mail para {email} com a senha {password}")

        # 🔥 Se quiser remover o job do Redis após processá-lo
        redis_client.delete(job_key)

  else:
    time.sleep(1)
    print("🔄 Nenhum job encontrado, aguardando...")
