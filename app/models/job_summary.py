from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base
from sqlalchemy.orm import relationship

class JobSummary(Base):
    __tablename__ = "job_summaries"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False, unique=True, index=True)
    total_spend_inr = Column(Float, nullable=True)
    total_spend_usd = Column(Float, nullable=True)
    top_merchants = Column(JSONB, nullable=True)
    anomaly_count = Column(Integer, nullable=True)
    narrative = Column(String, nullable=True)
    risk_level = Column(String, nullable=True)

    job = relationship("Job", back_populates="summary")
