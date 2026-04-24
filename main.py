from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os
import json

import database
from agents.extractor import extract_info

# Load environment variables
load_dotenv()

# Create the database tables
database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Z-Clear Trade Compliance Middleware")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

STATUS_MAPPING = {
    "RECEIVED": {"zh": "已接收", "en": "Received", "ms": "Diterima"},
    "EXTRACTING": {"zh": "提取中", "en": "Extracting", "ms": "Sedang Mengekstrak"},
    "AUDITING": {"zh": "审计中", "en": "Auditing", "ms": "Sedang Diaudit"},
    "PENDING_REMEDY": {"zh": "需补全", "en": "Pending Remedy", "ms": "Menunggu Pembaikan"},
    "COMPLETED": {"zh": "处理完成", "en": "Completed", "ms": "Selesai"},
    "INCOMPLETE": {"zh": "不完整", "en": "Incomplete", "ms": "Tidak Lengkap"},
    "ERROR": {"zh": "处理异常", "en": "Error", "ms": "Ralat"}
}

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

@app.post("/extract")
def extract_document(request: ProcessRequest, db: Session = Depends(get_db)):
    # 1. 状态初始化：创建 RECEIVED 记录
    state = database.SessionState(
        session_id=request.session_id, 
        status="RECEIVED", 
        raw_text=request.text
    )
    db.add(state)
    db.commit()
    
    # 2. 更新状态为 EXTRACTING
    database.update_session_status(db, request.session_id, "EXTRACTING")
    
    try:
        # 调用大模型提取
        extracted_data, _ = extract_info(request.text)
        
        # 3. 提取成功后，存入 JSON 并更新为 AUDITING
        extracted_dict = extracted_data.model_dump()
        state.extracted_json = json.dumps(extracted_dict)
        state.progress = json.dumps(extracted_dict) # Keep backward compatibility
        database.update_session_status(db, request.session_id, "AUDITING")
        
        # 4. 流程结束时，更新为 COMPLETED
        database.update_session_status(db, request.session_id, "COMPLETED")
        
        db.refresh(state)
        return {
            "session_id": state.session_id,
            "status": state.status,
            "progress": extracted_dict,
            "display_status": STATUS_MAPPING.get(state.status, STATUS_MAPPING["COMPLETED"])
        }
    except Exception as e:
        error_msg = str(e)
        state.audit_report = json.dumps({"error": error_msg})
        database.update_session_status(db, request.session_id, "ERROR")
        db.refresh(state)
        return {
            "session_id": state.session_id,
            "status": state.status,
            "progress": {},
            "display_status": STATUS_MAPPING["ERROR"],
            "error": error_msg
        }

@app.get("/session/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    state = db.query(database.SessionState).filter(database.SessionState.session_id == session_id).first()
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    progress_dict = json.loads(state.progress) if state.progress else {}
    extracted_json_dict = json.loads(state.extracted_json) if state.extracted_json else {}
    
    return {
        "session_id": state.session_id,
        "status": state.status,
        "raw_text": state.raw_text,
        "extracted_json": extracted_json_dict,
        "audit_report": json.loads(state.audit_report) if state.audit_report else None,
        "progress": progress_dict,
        "display_status": STATUS_MAPPING.get(state.status, {})
    }
