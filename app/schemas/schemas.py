from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any, Dict
from datetime import datetime

class TransactionBase(BaseModel):
    txn_id: Optional[str] = None
    date: Optional[datetime] = None
    merchant: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    category: Optional[str] = None
    account_id: Optional[str] = None
    notes: Optional[str] = None
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None
    llm_category: Optional[str] = None
    llm_raw_response: Optional[str] = None
    llm_failed: bool = False

class TransactionResponse(TransactionBase):
    id: int
    job_id: str

    model_config = ConfigDict(from_attributes=True)

class JobSummaryBase(BaseModel):
    total_spend_inr: Optional[float] = None
    total_spend_usd: Optional[float] = None
    top_merchants: Optional[Any] = None
    anomaly_count: Optional[int] = None
    narrative: Optional[str] = None
    risk_level: Optional[str] = None

class JobSummaryResponse(JobSummaryBase):
    id: int
    job_id: str

    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    filename: str
    status: str
    row_count_raw: Optional[int] = None
    row_count_clean: Optional[int] = None

class JobResponse(JobBase):
    id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    row_count_raw: Optional[int] = None
    row_count_clean: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class JobResultsResponse(BaseModel):
    job: JobResponse
    summary: Optional[JobSummaryResponse] = None
    cleaned_transactions: List[TransactionResponse] = []
    anomalies: List[TransactionResponse] = []
    category_breakdown: Optional[Dict[str, int]] = None
