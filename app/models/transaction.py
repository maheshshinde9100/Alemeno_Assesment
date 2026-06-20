from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    txn_id = Column(String)
    date = Column(DateTime(timezone=True))
    merchant = Column(String)
    amount = Column(Numeric(precision=10, scale=2))
    currency = Column(String(3))
    status = Column(String)
    category = Column(String)
    account_id = Column(String)
    notes = Column(Text)
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(Text)
    llm_category = Column(String)
    llm_raw_response = Column(Text)
    llm_failed = Column(Boolean, default=False)

    job = relationship("Job", back_populates="transactions")

