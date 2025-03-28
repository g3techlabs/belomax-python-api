from rq import Queue, Worker
from redis import Redis

# Conexão com o Redis
redis_conn = Redis(host='localhost', port=6379)
queue = Queue('users-queue', connection=redis_conn)

# A função precisa aceitar os mesmos parâmetros do job
def send_credentials_email_python(email, password):
    print("\n🔥 Recebi um novo job!")
    print(f"📧 Email: {email}, 🔑 Password: {password}")
    print("✅ Job processado com sucesso!\n")

if __name__ == '__main__':
    print("👷‍♂️ Worker aguardando jobs...")

    # Registrar a função para o worker poder chamá-la
    import sys
    sys.modules[__name__] = __import__(__name__)  # Registra funções no namespace

    worker = Worker([queue], connection=redis_conn)
    worker.work()
