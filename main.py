from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

import database

# Load environment variables
load_dotenv()

# Create the database tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Z-Clear Trade Compliance Middleware")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/status")
def get_status(db: Session = Depends(get_db)):
    return {
        "status": "ok", 
        "message": "Z-Clear Trade Compliance Middleware is running",
        "api_key_configured": os.getenv("ZHIPU_API_KEY") is not None and os.getenv("ZHIPU_API_KEY") != "your_key_here"
    }
