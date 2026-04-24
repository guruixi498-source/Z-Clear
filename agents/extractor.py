import os
import json
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import database models from parent directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import SessionState

load_dotenv()

class ExtractedData(BaseModel):
    item_name: Optional[str] = Field(None, description="The name of the item/product (品名)")
    hs_code: Optional[str] = Field(None, description="The customs HS code (海关编码)")
    weight: Optional[str] = Field(None, description="The weight of the item (重量)")

def extract_info(text: str) -> tuple[ExtractedData, str]:
    """
    Extracts key information from text using OpenAI.
    Returns the extracted data and the status (COMPLETED or INCOMPLETE).
    """
    client = OpenAI(
        api_key=os.getenv("ILMU_API_KEY"), 
        base_url=os.getenv("ILMU_API_BASE")
    )
    
    prompt = f"""
    Please extract the following information from the text below:
    - item_name (品名)
    - hs_code (海关编码)
    - weight (重量)
    
    Return ONLY a valid JSON object matching this schema:
    {{"item_name": "string or null", "hs_code": "string or null", "weight": "string or null"}}
    
    Text:
    {text}
    """
    
    try:
        print("开始调用 ILMU API...")
        response = client.chat.completions.create(
            model="nemo-super",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant. Always output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        print("ILMU API 返回结果成功！")
        
        content = response.choices[0].message.content
        # Remove potential markdown formatting
        content = content.replace("```json", "").replace("```", "").strip()
        data_dict = json.loads(content)
        extracted = ExtractedData(**data_dict)
        
        # Check for missing critical fields (item_name, hs_code, weight)
        if not extracted.item_name or not extracted.hs_code or not extracted.weight:
            status = "INCOMPLETE"
        else:
            status = "COMPLETED"
            
        return extracted, status
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        return ExtractedData(), "INCOMPLETE"


def process_and_store_document(session_id: str, text: str, db: Session) -> dict:
    """
    Extracts info from text and stores it in the database under the given session_id.
    Creates a new session if one doesn't exist.
    """
    # 1. Extract data
    extracted_data, status = extract_info(text)
    
    # 2. Convert extracted data to dict/json
    progress_dict = extracted_data.model_dump()
    progress_json = json.dumps(progress_dict)
    
    # 3. Retrieve or create session state
    state = db.query(SessionState).filter(SessionState.session_id == session_id).first()
    
    if not state:
        state = SessionState(session_id=session_id)
        db.add(state)
    
    # 4. Update the state
    state.progress = progress_json
    state.status = status
    
    # 5. Commit changes
    db.commit()
    db.refresh(state)
    
    return {
        "session_id": state.session_id,
        "status": state.status,
        "progress": progress_dict
    }
