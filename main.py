from dotenv import load_dotenv
from core.redis_queue.consumer import redis_consumer
from core.automations.pensioner_paycheck.main import trigger_pensioner_paycheck
from core.automations.statement_extract.main import trigger_statement_extract

load_dotenv()

if (__name__ == "__main__"):
  def handle_job(job_name, job_payload):
    if job_name == "fetch-pensioner-paycheck":
      result = trigger_pensioner_paycheck(job_payload)
      print("Automation result:", result)
    elif job_name == "new-statement-extract":
      trigger_statement_extract(job_payload)

  redis_consumer("belomax-queue", handle_job)