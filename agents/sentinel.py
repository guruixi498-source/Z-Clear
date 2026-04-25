import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import text
from dotenv import load_dotenv
import sys

# Import database models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database

load_dotenv()

class RetrieveRequest(BaseModel):
    hs_code: str = Field(..., description="HS code")
    product_name: str = Field(..., description="Product name")
    import_country: str = Field(..., description="Import country")
    export_country: str = Field(..., description="Export country")

class RegulationResult(BaseModel):
    title: str
    content: str
    hs_code: str
    applicable_country: str

class RetrieveResponse(BaseModel):
    status: str
    query_context: str = ""
    matched_regulations: List[RegulationResult] = []
    generated_analysis: str = ""
    error: str = ""

def get_openai_client():
    return OpenAI(
        api_key=os.getenv("ILMU_API_KEY", "dummy"), 
        base_url=os.getenv("ILMU_API_BASE", "https://api.example.com/v1")
    )

def generate_embedding(text_input: str) -> List[float]:
    """Generate vector embeddings using embedding-3."""
    client = get_openai_client()
    try:
        response = client.embeddings.create(
            model="embedding-3",
            input=text_input
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        # Return a dummy vector of 2048 dimensions if API fails (for testing)
        return [0.0] * 2048

def retrieve_regulations(db: Session, hs_code: str, product_name: str, import_country: str, export_country: str) -> List[database.ComplianceRegulation]:
    """
    Retrieve top 3 regulations using MariaDB VEC_DISTANCE_COSINE function.
    """
    query_text = f"HS Code: {hs_code}, Product: {product_name}, Trade Route: {export_country} to {import_country}"
    query_vector = generate_embedding(query_text)
    
    # Format the vector for MariaDB VEC_FromText
    vector_str = "[" + ",".join(map(str, query_vector)) + "]"
    
    # Raw SQL to utilize MariaDB's Vector engine
    # SQLite fallback is provided for testing environment
    engine_name = db.get_bind().dialect.name
    
    if engine_name == "sqlite":
        # Mock behavior for SQLite environment since it doesn't support VEC_DISTANCE_COSINE
        # We just return the first 3 regulations or an empty list
        print("Running in SQLite mode, mocking VEC_DISTANCE_COSINE...")
        return db.query(database.ComplianceRegulation).limit(3).all()
        
    # MariaDB specific query
    sql = text('''
        SELECT id, title, content, hs_code, applicable_country
        FROM compliance_regulation
        ORDER BY VEC_DISTANCE_COSINE(vector_data, VEC_FromText(:vector_str))
        LIMIT 3
    ''')
    
    result = db.execute(sql, {"vector_str": vector_str})
    
    regulations = []
    for row in result:
        reg = database.ComplianceRegulation(
            id=row[0],
            title=row[1],
            content=row[2],
            hs_code=row[3],
            applicable_country=row[4]
        )
        regulations.append(reg)
        
    return regulations

def generate_rag_analysis(context: str, hs_code: str, product_name: str) -> str:
    """Generate analysis using glm-4, strictly based on context."""
    client = get_openai_client()
    prompt = f"""
    You are a Trade Compliance Sentinel Agent.
    Based strictly on the following regulations context, analyze the compliance for the product "{product_name}" with HS code "{hs_code}".
    Do not invent or hallucinate any rules or policies. If the context is empty, say "No relevant regulations found."
    
    Context:
    {context}
    """
    
    try:
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "You are a strict compliance AI. Answer ONLY based on provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating analysis: {e}"

def run_sentinel_agent(db: Session, session_id: str, extracted_data: dict) -> dict:
    """
    Execute the Sentinel Agent logic for a given session.
    """
    hs_code = extracted_data.get("hs_code", "")
    product_name = extracted_data.get("item_name", "")
    
    # We might not have country info extracted, using defaults or placeholders if not present
    import_country = extracted_data.get("import_country", "Unknown")
    export_country = extracted_data.get("export_country", "Unknown")
    
    state = db.query(database.SessionState).filter(database.SessionState.session_id == session_id).first()
    if not state:
        return {"status": "ERROR", "error": "Session not found"}
        
    try:
        regs = retrieve_regulations(db, hs_code, product_name, import_country, export_country)
        
        context_parts = []
        matched = []
        for reg in regs:
            context_parts.append(f"Title: {reg.title}\\nContent: {reg.content}\\nApplicable to: {reg.applicable_country}")
            matched.append({
                "title": reg.title,
                "content": reg.content,
                "hs_code": reg.hs_code,
                "applicable_country": reg.applicable_country
            })
            
        context_str = "\\n\\n".join(context_parts)
        analysis = generate_rag_analysis(context_str, hs_code, product_name)
        
        audit_report = {
            "sentinel_analysis": analysis,
            "matched_regulations": matched
        }
        
        state.audit_report = json.dumps(audit_report)
        
        # Note: According to PRD, update status to AUDITING. 
        # (It's already AUDITING from /extract, but we ensure it here)
        state.status = "AUDITING"
        db.commit()
        
        return {
            "status": "SUCCESS",
            "analysis": analysis,
            "matched_regulations": matched
        }
    except Exception as e:
        error_msg = str(e)
        state.status = "ERROR"
        state.error_log = error_msg
        db.commit()
        return {"status": "ERROR", "error": error_msg}
