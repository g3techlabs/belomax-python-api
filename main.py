from dotenv import load_dotenv
from core.redis_queue.consumer import redis_consumer

load_dotenv()

if (__name__ == "__main__"):
  redis_consumer("users-queue")