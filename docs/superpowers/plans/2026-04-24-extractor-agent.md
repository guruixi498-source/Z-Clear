# Extractor Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an extraction agent that extracts `item_name`, `hs_code`, and `weight` from unstructured text, marking the status as `INCOMPLETE` if key fields are missing, and storing the results into the `SessionState` table in the SQLite database.

**Architecture:** The implementation uses a Pydantic model for structured LLM output (via ZhipuAI). It includes a main extraction function that queries the model, validates the presence of critical fields, calculates the final status (`COMPLETED` vs `INCOMPLETE`), and persists the updated JSON progress back to the SQLAlchemy database using the existing `database.py` models.

**Tech Stack:** Python, ZhipuAI (GLM-4), Pydantic, SQLAlchemy, JSON

---

## Bite-Sized Tasks

### Task 1: Create structured output models for extraction

**Files:**
- Create: `agents/extractor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extractor.py
import pytest
from agents.extractor import ExtractedData

def test_extracted_data_model():
    data = ExtractedData(item_name="Steel Pipe", hs_code="7304", weight="500kg")
    assert data.item_name == "Steel Pipe"
    assert data.hs_code == "7304"
    assert data.weight == "500kg"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_extractor.py::test_extracted_data_model -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'agents'"

- [ ] **Step 3: Write minimal implementation**

```python
# agents/__init__.py
# (Empty file to make it a package)

# agents/extractor.py
from pydantic import BaseModel, Field
from typing import Optional

class ExtractedData(BaseModel):
    item_name: Optional[str] = Field(None, description="The name of the item/product (品名)")
    hs_code: Optional[str] = Field(None, description="The customs HS code (海关编码)")
    weight: Optional[str] = Field(None, description="The weight of the item (重量)")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_extractor.py::test_extracted_data_model -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/__init__.py agents/extractor.py tests/test_extractor.py
git commit -m "feat: add pydantic model for extraction data"
```

### Task 2: Implement core LLM extraction logic using ZhipuAI

**Files:**
- Modify: `agents/extractor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extractor.py
import json
from unittest.mock import patch, MagicMock
from agents.extractor import extract_info

@patch('agents.extractor.ZhipuAI')
def test_extract_info_mocked(mock_zhipu):
    # Setup mock response
    mock_client = MagicMock()
    mock_zhipu.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content='{"item_name": "Steel Pipe", "hs_code": "7304", "weight": "500kg"}'))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    result, status = extract_info("Dummy invoice text")
    
    assert result.item_name == "Steel Pipe"
    assert result.weight == "500kg"
    assert status == "COMPLETED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_extractor.py::test_extract_info_mocked -v`
Expected: FAIL with "ImportError: cannot import name 'extract_info'"

- [ ] **Step 3: Write minimal implementation**

```python
# Modify agents/extractor.py to append:
import os
import json
from zhipuai import ZhipuAI
from dotenv import load_dotenv

load_dotenv()

def extract_info(text: str) -> tuple[ExtractedData, str]:
    """
    Extracts key information from text using ZhipuAI.
    Returns the extracted data and the status (COMPLETED or INCOMPLETE).
    """
    api_key = os.getenv("ZHIPU_API_KEY")
    client = ZhipuAI(api_key=api_key)
    
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
        response = client.chat.completions.create(
            model="glm-4",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant. Always output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_extractor.py::test_extract_info_mocked -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/extractor.py tests/test_extractor.py
git commit -m "feat: implement ZhipuAI extraction logic and status evaluation"
```

### Task 3: Implement database integration for storing extracted results

**Files:**
- Modify: `agents/extractor.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_extractor.py
from agents.extractor import process_and_store_document
import database
import json

def test_process_and_store_document(monkeypatch):
    # Setup in-memory DB for test
    database.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    
    # Create initial session state
    state = database.SessionState(session_id="test-session-123", progress="{}", status="initialized")
    db.add(state)
    db.commit()
    
    # Mock extract_info to avoid API call
    from agents.extractor import ExtractedData
    def mock_extract(text):
        return ExtractedData(item_name="Test", hs_code="123", weight=None), "INCOMPLETE"
    
    monkeypatch.setattr("agents.extractor.extract_info", mock_extract)
    
    # Run the function
    process_and_store_document("test-session-123", "Some text missing weight", db)
    
    # Verify DB update
    updated_state = db.query(database.SessionState).filter_by(session_id="test-session-123").first()
    progress = json.loads(updated_state.progress)
    
    assert updated_state.status == "INCOMPLETE"
    assert progress["item_name"] == "Test"
    assert progress["weight"] is None
    
    db.close()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_extractor.py::test_process_and_store_document -v`
Expected: FAIL with "ImportError: cannot import name 'process_and_store_document'"

- [ ] **Step 3: Write minimal implementation**

```python
# Modify agents/extractor.py to append:
from sqlalchemy.orm import Session
from database import SessionState

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_extractor.py::test_process_and_store_document -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add agents/extractor.py tests/test_extractor.py
git commit -m "feat: add function to process and store extraction results in db"
```

## Self-Review Checklist

- [x] Spec coverage: Extraction logic covers `item_name`, `hs_code`, `weight`. Status set to `INCOMPLETE` if missing. Stores results in `SessionState` via SQLite.
- [x] Placeholders: No placeholders used, full code implementations provided.
- [x] Type consistency: `ExtractedData` used consistently. `SessionState` fields align with `database.py`.
