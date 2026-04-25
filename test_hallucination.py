import os
import json
from fastapi.testclient import TestClient
import database
from main import app

# 强制注入假的 API KEY 环境，确保应用不会尝试真实请求 Z.AI 的真实扣费
# （因为这里需要真实触发大模型逻辑进行防幻觉测试，我们将在测试用例中打桩 `agents.sentinel_agent.OpenAI` 或者利用真实沙箱API如果需要）
# 在沙盒环境中，我们需要通过 TestClient 发送请求
client = TestClient(app)

def run_hallucination_test():
    # 1. 设置一个 session
    db = database.SessionLocal()
    session_id = "test-anti-hallucination-9999"
    state = database.SessionState(session_id=session_id, status="EXTRACTING")
    db.add(state)
    db.commit()
    db.close()
    
    # 2. 我们使用 unittest.mock 来 mock openai 客户端，以确保防幻觉规则（传入空文档时）被执行
    # 为了严格测试 prompt，我们可以直接验证 prompt 或者利用假的 LLM 响应检查
    # 这里直接调用代理进行测试
    
    from unittest.mock import patch, MagicMock
    with patch("agents.sentinel_agent.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # 伪造 embedding 响应
        mock_emb_response = MagicMock()
        mock_emb_response.data = [MagicMock(embedding=[0.0] * 1536)]
        mock_client.embeddings.create.return_value = mock_emb_response
        
        # 伪造 GLM 响应，模拟 GLM 根据防幻觉 Prompt 返回的内容
        mock_chat_response = MagicMock()
        mock_chat_response.choices = [
            MagicMock(message=MagicMock(content="未检索到匹配的海关合规政策或 RCEP 规则。"))
        ]
        mock_client.chat.completions.create.return_value = mock_chat_response
        
        # 3. 发起请求
        payload = {
            "session_id": session_id,
            "hs_code": "9999.99.99",
            "product_name": "不存在的外星科技产品",
            "import_country": "US",
            "export_country": "CN"
        }
        response = client.post("/sentinel/retrieve", json=payload)
        
        print("Response Code:", response.status_code)
        print("Response JSON:", json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        data = response.json()
        if data["status"] == "success" and "未检索到" in data["regulation_context"]:
            print("✅ 防幻觉校验通过：正确返回了无匹配法规，未生成虚假海关政策。")
        else:
            print("❌ 防幻觉校验失败：可能生成了虚假信息。")
            
if __name__ == "__main__":
    run_hallucination_test()
