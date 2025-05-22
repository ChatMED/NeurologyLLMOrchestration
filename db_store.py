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


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)


class Metric(Base):
    __tablename__ = "metrics"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    text = Column(Text, nullable=False)

    metric = relationship("Metric", back_populates="questions")


Metric.questions = relationship("Question", back_populates="metric", cascade="all, delete-orphan")


class ReportKey(Base):
    __tablename__ = "report_keys"
    id = Column(Integer, primary_key=True)
    key_path = Column(String, nullable=False, unique=True)  # e.g., "summary.findings.brain_volume"


class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    predicted_report_id = Column(Integer, ForeignKey("predicted_neurology_reports.id"), nullable=False)
    report_key_id = Column(Integer, ForeignKey("report_keys.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    # Either a numeric score or a comment, or both
    rating = Column(Integer, nullable=True)  # 1 to 10
    comment = Column(Text, nullable=True)

    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    predicted_report = relationship("PredictedNeurologyReportRecord")
    report_key = relationship("ReportKey")
    question = relationship("Question")


# Connection string format: 'postgresql://user:password@host:port/database'
server = os.getenv("DB_SERVER", "localhost")
port = os.getenv("DB_PORT", "5433")
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
