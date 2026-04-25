import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import os
os.environ["ILMU_API_KEY"] = "fake-key"
os.environ["ILMU_API_BASE"] = "https://fake.url"

import database
from main import app
from agents.sentinel_agent import SentinelAgent

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    # 确保数据库被重新创建
    database.Base.metadata.drop_all(bind=database.engine)
    database.Base.metadata.create_all(bind=database.engine)
    yield
    database.Base.metadata.drop_all(bind=database.engine)

@pytest.fixture
def db_session():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_insert_and_retrieve_regulation(db_session: Session):
    # 法规插入测试
    test_embedding = [0.1] * 1536
    reg = database.insert_regulation(
        db=db_session,
        title="Test Regulation",
        content="Test Content",
        country="CN",
        embedding=test_embedding,
        hs_code="1234"
    )
    
    assert reg.id is not None
    assert reg.title == "Test Regulation"
    
    # 向量检索测试 (Fallback SQLite 会根据 hs_code 精准返回)
    results = database.search_similar_regulations(
        db=db_session,
        query_embedding=[0.1]*1536,
        top_k=1,
        hs_code="1234"
    )
    assert len(results) > 0
    assert results[0]["title"] == "Test Regulation"
    assert results[0]["hs_code"] == "1234"

@patch("agents.sentinel_agent.OpenAI")
def test_sentinel_agent_execute(mock_openai, db_session: Session):
    # 接口调用测试 & Agent执行测试
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    
    # Mock embeddings response
    mock_emb_response = MagicMock()
    mock_emb_response.data = [MagicMock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_emb_response
    
    # Mock chat response
    mock_chat_response = MagicMock()
    mock_chat_response.choices = [
        MagicMock(message=MagicMock(content="模拟的合规指导上下文"))
    ]
    mock_client.chat.completions.create.return_value = mock_chat_response

    # Initialize agent
    agent = SentinelAgent(db_session)
    result = agent.execute(
        hs_code="1234",
        product_name="Test Product",
        import_country="US",
        export_country="CN"
    )
    
    assert "compliance_context" in result
    assert result["compliance_context"] == "模拟的合规指导上下文"
    assert "retrieved_regulations" in result

def test_api_endpoint_success(db_session: Session):
    # 先创建一个 session
    session_id = "test-sentinel-1"
    state = database.SessionState(session_id=session_id, status="EXTRACTING")
    db_session.add(state)
    db_session.commit()
    
    # Mock 掉 SentinelAgent 的 execute 方法
    with patch.object(SentinelAgent, 'execute', return_value={"compliance_context": "测试上下文", "retrieved_regulations": []}):
        response = client.post("/sentinel/retrieve", json={
            "session_id": session_id,
            "hs_code": "1234",
            "product_name": "Test Product",
            "import_country": "US",
            "export_country": "CN"
        })
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["regulation_context"] == "测试上下文"
    
    # 验证数据库状态更新
    updated_state = db_session.query(database.SessionState).filter_by(session_id=session_id).first()
    assert updated_state.status == "AUDITING"
    assert updated_state.regulation_context == "测试上下文"

def test_api_endpoint_error_handling(db_session: Session):
    # 异常场景测试
    session_id = "test-sentinel-error"
    state = database.SessionState(session_id=session_id, status="EXTRACTING")
    db_session.add(state)
    db_session.commit()
    
    # 模拟执行时抛出异常
    with patch.object(SentinelAgent, 'execute', side_effect=Exception("模拟的测试异常")):
        response = client.post("/sentinel/retrieve", json={
            "session_id": session_id,
            "hs_code": "1234",
            "product_name": "Test Product",
            "import_country": "US",
            "export_country": "CN"
        })
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "error"
    assert "模拟的测试异常" in data["error_log"]
    
    # 验证数据库状态更新为 ERROR 并记录了错误日志
    updated_state = db_session.query(database.SessionState).filter_by(session_id=session_id).first()
    assert updated_state.status == "ERROR"
    assert "模拟的测试异常" in updated_state.error_log
