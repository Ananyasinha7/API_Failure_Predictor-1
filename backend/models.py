from fastapi import FastAPI
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, CheckConstraint
from .database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.types import Enum
from enum import Enum as PyEnum


class MethodEnum(PyEnum):
    GET="GET"
    POST="POST"
    PUT="PUT"
    DELETE="DELETE"
    PATCH="PATCH"


class Logs(Base):
    __tablename__="failure_logs"
    id= Column(Integer,primary_key=True, index=True)
    service_name=Column(String, nullable=False, index=True)
    endpoint=Column(String, nullable=False, index=True)
    method=Column(Enum(MethodEnum), nullable=False) 
    status_code=Column(Integer, nullable=False)
    response_time=Column(Float, nullable=False)
    timestamp=Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    __table_args__ = (
        CheckConstraint('status_code >= 100 AND status_code <= 599', name='status_code_valid_range'),
    )


class APIFeatures(Base):
    __tablename__="api_features"
    id= Column(Integer,primary_key=True, index=True)
    service_name=Column(String, index=True, nullable=False)
    endpoint=Column(String, index=True, nullable=False)
    window_start=Column(DateTime, nullable=False, index=True)
    window_end=Column(DateTime, nullable=False, index=True)
    total_requests=Column(Integer, nullable=False)
    error_count=Column(Integer, nullable=False)
    error_rate=Column(Float, nullable=False)
    avg_response_time=Column(Float, nullable=False)
    max_response_time=Column(Float, nullable=False)
    p95_response_time=Column(Float, nullable=False)
    created_at=Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    __table_args__=(
        CheckConstraint('error_rate >= 0.0 AND error_rate <= 1.0', name='error_rate_valid_range'),
    )


class RiskScores(Base):
    __tablename__="risk_scores"
    id=Column(Integer, primary_key=True, index=True)
    service_name=Column(String, index=True, nullable=False)
    endpoint=Column(String, index=True, nullable=False)
    window_start=Column(DateTime, nullable=False, index=True)
    risk_score=Column(Float, nullable=False)
    model_version=Column(String, nullable=False)
    created_at=Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    __table_args__=(
        CheckConstraint('risk_score>=0.0 AND risk_score <=1.0', name='risk_score_valid_range'),
    )


