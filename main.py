from dotenv import load_dotenv
from core.redis_queue.consumer import redis_consumer
from core.automations.pensioner_paycheck.main import trigger_pensioner_paycheck

load_dotenv()

if (__name__ == "__main__"):
  def handle_job(job_name, job_payload):
    if job_name == "fetch-pensioner-paycheck":
      result = trigger_pensioner_paycheck(job_payload)
      print("Automation result:", result)

  redis_consumer("users-queue", handle_job)