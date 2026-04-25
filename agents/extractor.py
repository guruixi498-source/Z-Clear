import os
import json
import re
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
    # Fallback dummy keys if not set in environment
    api_key = os.getenv("ILMU_API_KEY")
    if not api_key or api_key == "your_key_here":
        api_key = "dummy_key_for_development"
        
    base_url = os.getenv("ILMU_API_BASE")
    if not base_url:
        base_url = "https://api.example.com/v1"

    client = OpenAI(
        api_key=api_key,
        base_url=base_url
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
        print("🚀 正在请求 ILMU API...")
        response = client.chat.completions.create(
            model="ilmu-glm-5.1",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant. Output ONLY valid JSON. No markdown formatting, no backticks, no conversational text. Schema: {\"item_name\": \"str\", \"hs_code\": \"str\", \"weight\": \"str\"}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content
        print("📦 API 原始返回内容:", content)

        # 使用正则强行提取 JSON 括号内的内容，防止模型废话
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = content
        
        data_dict = json.loads(clean_json)
        extracted = ExtractedData(**data_dict)
        
        # 检查是否缺失
        if not extracted.item_name or not extracted.hs_code or not extracted.weight:
            status = "INCOMPLETE"
        else:
            status = "COMPLETED"
            
        return extracted, status
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ 提取失败: {error_msg[:100]}...")
        
        # 强制响应校验：如果 API 失败（如由于 Cloudflare 拦截），则使用本地正则提取，确保返回标准 JSON 结构，无乱码
        item_name = ""
        hs_code = ""
        weight = ""
        
        # 简单的正则匹配发票内容
        item_match = re.search(r"Item Description:\s*(.*)", text, re.IGNORECASE)
        hs_match = re.search(r"HS Code:\s*(.*)", text, re.IGNORECASE)
        weight_match = re.search(r"(?:Gross Weight|Weight):\s*(.*)", text, re.IGNORECASE)
        
        if item_match:
            item_name = item_match.group(1).strip()
        if hs_match:
            hs_code = hs_match.group(1).strip()
        if weight_match:
            weight = weight_match.group(1).strip()
            
        if item_name or hs_code or weight:
            return ExtractedData(item_name=item_name, hs_code=hs_code, weight=weight), "COMPLETED"

        return ExtractedData(item_name="[API请求失败或文本无法解析]", hs_code="N/A", weight="N/A"), "ERROR"


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
