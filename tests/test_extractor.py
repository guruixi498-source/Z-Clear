import pytest
import json
from unittest.mock import patch, MagicMock
from agents.extractor import ExtractedData, extract_info, process_and_store_document
import database

def test_extracted_data_model():
    data = ExtractedData(item_name="Steel Pipe", hs_code="7304", weight="500kg")
    assert data.item_name == "Steel Pipe"
    assert data.hs_code == "7304"
    assert data.weight == "500kg"

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

def test_process_and_store_document(monkeypatch):
    # Setup in-memory DB for test
    database.Base.metadata.create_all(bind=database.engine)
    db = database.SessionLocal()
    
    # Create initial session state
    state = database.SessionState(session_id="test-session-123", progress="{}", status="initialized")
    db.add(state)
    db.commit()
    
    # Mock extract_info to avoid API call
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
