from sqlalchemy import Column, Integer, Numeric, ForeignKey, JSON, Text, String
from sqlalchemy.orm import relationship
from app.db import Base
import enum


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class JobSummary(Base):
    __tablename__ = "job_summaries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, unique=True)
    total_spend_inr = Column(Numeric(precision=12, scale=2))
    total_spend_usd = Column(Numeric(precision=12, scale=2))
    top_merchants = Column(JSON)
    anomaly_count = Column(Integer)
    narrative = Column(Text)
    risk_level = Column(String)

    job = relationship("Job", back_populates="summary")

