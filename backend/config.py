from dotenv import load_dotenv
import os

if os.getenv("APP_ENV") != "prod":
    load_dotenv()

class Config:
    def __init__(self):
        self.RISK_API_KEY=os.getenv("RISK_API_KEY")
        self.APP_ENV=(os.getenv("APP_ENV") or "").lower()
        self.MODEL_PATH=os.getenv("MODEL_PATH")
        self.LOG_LEVEL=os.getenv("LOG_LEVEL")
        self.SQLALCHEMY_DATABASE_URL=os.getenv("SQLALCHEMY_DATABASE_URL")
        
        self._validate()

    def _validate(self): 
        required_vars=["RISK_API_KEY","APP_ENV","MODEL_PATH","SQLALCHEMY_DATABASE_URL"]
        optional_vars=["LOG_LEVEL"]
        missing_vars=[]
        for key,value in vars(self).items():
            if key in required_vars:
                 if value is None:
                    missing_vars.append(key)
                 elif value.strip()=="":
                    missing_vars.append(key)
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")


config=Config()

