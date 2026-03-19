from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

app=FastAPI()

class RiskScoreResponse(BaseModel):
    id: int
    service_name: str
    endpoint: str
    risk_score: float
    created_at: datetime
    class Config:
        orm_mode = True

class RiskSummaryResponse(BaseModel):
    endpoint: str
    avg_risk_score: float
    max_risk_score: float
    min_risk_score: float
    class Config:
        orm_mode = True