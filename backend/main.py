from fastapi import FastAPI, HTTPException
from .database import Base, engine
from .logging_middleware import logging_middleware
import uvicorn
import asyncio
from .config import config
from .logging_config import setup_logging
from .startup_checks import check_required_env_vars
from ml_backend.model_initialization import ensure_model_exists

app=FastAPI()
setup_logging()

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
async def startup_event():
    check_required_env_vars(["RISK_API_KEY", "APP_ENV", "MODEL_PATH", "SQLALCHEMY_DATABASE_URL"])
    ensure_model_exists(config.MODEL_PATH)


@app.middleware("http") 
async def log_requests(request,call_next):
    return await logging_middleware(request, call_next) 

@app.get("/")
async def normal_endpoint():
    return {"message": "This is a normal endpoint."}

@app.get("/slow")
async def slow_endpoint():
    await asyncio.sleep(2)
    return {"message": "This is a slow endpoint."}

@app.get("/failure")
async def failure_endpoint():
    raise HTTPException(status_code=500, detail="Simulated failure for testing logging.")


if __name__=="__main__":
   
    uvicorn.run(app, host="127.0.0.1", port=8000)
