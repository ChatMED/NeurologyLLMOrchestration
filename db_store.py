import os

from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

from models import NeurologyReport

# SQLAlchemy setup
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ReportSummary(BaseModel):
    id: int
    name: str
    created_at: datetime
    summary: str
    full_report: dict
    class Config:
        from_attributes = True


class PredictedNeurologyReportRecord(Base):
    __tablename__ = 'predicted_neurology_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    summary = Column(Text, nullable=False)
    full_report = Column(JSONB, nullable=False)
    real_report_id = Column(Integer, ForeignKey("neurology_reports.id"), nullable=True)
    real_report = relationship("NeurologyReportRecord", back_populates="generated_reports")

class NeurologyReportRecord(Base):
    __tablename__ = 'neurology_reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.now())
    summary = Column(Text, nullable=False)
    full_report = Column(JSONB, nullable=False)

    # Backref from NeurologyReportRecord
    generated_reports = relationship("PredictedNeurologyReportRecord", back_populates="real_report")


# Connection string format: 'postgresql://user:password@host:port/database'
server = os.getenv("DB_SERVER","localhost")
port = os.getenv("DB_PORT","5433")
DATABASE_URL = f"postgresql://llm:llm@{server}:{port}/chatmed_pipeline"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create the table (if it doesn't exist)
Base.metadata.create_all(bind=engine)

def save_report_to_db(report: NeurologyReport):
    session = SessionLocal()
    try:
        db_record = PredictedNeurologyReportRecord(
            name=report.name,
            summary=report.compressed_summary,
            full_report=json.loads(report.json())
        )
        session.add(db_record)
        session.commit()
        session.refresh(db_record)
        print(f"Saved report with ID {db_record.id}")
    except Exception as e:
        session.rollback()
        print("Error saving report:", e)
    finally:
        session.close()
