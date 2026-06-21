from celery import shared_task
import time

@shared_task(name="process_transaction_job")
def process_transaction_job(job_id: str, file_path: str):
    # To be implemented in later prompts
    print(f"Processing job {job_id} for file {file_path}")
    pass
