from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

import database
from agents.extractor import process_and_store_document

# Load environment variables
load_dotenv()

# Create the database tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Z-Clear Trade Compliance Middleware")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

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
        "api_key_configured": os.getenv("ILMU_API_KEY") is not None and os.getenv("ILMU_API_KEY") != "your_key_here"
    }

class ProcessRequest(BaseModel):
    session_id: str
    text: str

@app.post("/process")
def process_document(request: ProcessRequest, db: Session = Depends(get_db)):
    result = process_and_store_document(
        session_id=request.session_id,
        text=request.text,
        db=db
    )
    return result
