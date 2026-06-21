from app.core.celery_app import celery_app
import pandas as pd
from datetime import datetime, timezone
import json

from app.db.database import SessionLocal
from app.models.job import Job
from app.models.transaction import Transaction
from app.models.job_summary import JobSummary

from app.services.csv_parser import REQUIRED_COLUMNS
from app.services.data_cleaner import clean_transactions
from app.services.anomaly_detector import detect_anomalies
from app.services.llm_classifier import classify_transactions_sync
from app.services.llm_summary import generate_summary_sync

@celery_app.task(bind=True, max_retries=3, default_retry_delay=5, name="process_transaction_job")

def process_transaction_job(self, job_id: str, file_path: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        db.close()
        return

    job.status = "processing"
    db.commit()

    try:
        # 2. Load CSV
        try:
            df = pd.read_csv(file_path)
            # Basic validation
            missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
            if missing:
                raise ValueError(f"Missing columns: {missing}")
        except Exception as e:
            raise ValueError(f"CSV read error: {str(e)}")

        # 3. Clean Data
        df = clean_transactions(df)
        job.row_count_clean = len(df)
        
        # 4. Anomaly Detection
        df = detect_anomalies(df)

        # 5. Classification (Missing Categories)
        uncategorised_mask = df['category'].isna() | (df['category'].astype(str).str.upper() == 'UNCATEGORISED')
        uncategorised_txns = df[uncategorised_mask].to_dict('records')
        
        if uncategorised_txns:
            try:
                # LLM call, if it fails, retry via Celery
                classifications = classify_transactions_sync(uncategorised_txns)
                class_dict = {item['txn_id']: item['category'] for item in classifications}
                
                # Apply classifications
                def apply_cat(row):
                    if row['txn_id'] in class_dict:
                        return class_dict[row['txn_id']]
                    return row['category']
                
                df['llm_category'] = df.apply(lambda r: class_dict.get(r['txn_id']), axis=1)
                df['category'] = df.apply(apply_cat, axis=1)
                df['llm_failed'] = False
                
            except Exception as exc:
                # Retry logic
                if self.request.retries < self.max_retries:
                    db.close()
                    raise self.retry(exc=exc)
                else:
                    # Mark batch as failed, continue
                    df['llm_failed'] = True
                    df['llm_category'] = None
        else:
            df['llm_failed'] = False
            df['llm_category'] = None

        # 6. Save Transactions
        df = df.where(pd.notnull(df), None) # Fix SQLAlchemy NaN issues
        txns_to_insert = []
        for _, row in df.iterrows():
            date_val = row['date'] if pd.notnull(row['date']) else None
            amount_val = row['amount'] if pd.notnull(row['amount']) else 0.0
            txns_to_insert.append(Transaction(
                job_id=job_id,
                txn_id=row.get('txn_id'),
                date=date_val,
                merchant=row.get('merchant'),
                amount=amount_val,
                currency=row.get('currency'),
                status=row.get('status'),
                category=row.get('category'),
                account_id=row.get('account_id'),
                notes=row.get('notes'),
                is_anomaly=row.get('is_anomaly', False),
                anomaly_reason=row.get('anomaly_reason'),
                llm_category=row.get('llm_category'),
                llm_failed=row.get('llm_failed', False)
            ))
        db.add_all(txns_to_insert)

        # 7. Generate Summary
        total_inr = df[df['currency'] == 'INR']['amount'].sum()
        total_usd = df[df['currency'] == 'USD']['amount'].sum()
        anomaly_count = int(df['is_anomaly'].sum())
        top_merchants = df['merchant'].value_counts().head(3).to_dict()

        stats = {
            "total_inr": float(total_inr),
            "total_usd": float(total_usd),
            "anomaly_count": anomaly_count,
            "top_merchants": top_merchants
        }

        # Try to generate narrative
        summary_data = generate_summary_sync(stats)

        # 8. Save summary
        summary = JobSummary(
            job_id=job_id,
            total_spend_inr=summary_data.get('total_spend_inr'),
            total_spend_usd=summary_data.get('total_spend_usd'),
            top_merchants=summary_data.get('top_merchants'),
            anomaly_count=summary_data.get('anomaly_count'),
            narrative=summary_data.get('narrative'),
            risk_level=summary_data.get('risk_level')
        )
        db.add(summary)

        # 10. Complete Job
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    finally:
        db.close()
