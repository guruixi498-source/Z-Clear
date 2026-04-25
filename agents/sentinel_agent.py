import os
import json
from openai import OpenAI
from sqlalchemy.orm import Session
import database

def get_glm_client():
    return OpenAI(
        api_key=os.getenv("ILMU_API_KEY", "dummy-key-for-test"), 
        base_url=os.getenv("ILMU_API_BASE", "https://dummy-base.com")
    )

class SentinelAgent:
    def __init__(self, db: Session):
        self.db = db
        self.client = get_glm_client()

    def generate_embedding(self, text: str) -> list[float]:
        """
        调用 embedding-3 模型生成向量。
        100%复用项目已封装好的API调用方式，转换为固定维度向量适配MariaDB Vector。
        """
        try:
            response = self.client.embeddings.create(
                model="embedding-3",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            # 捕获大模型调用异常
            raise Exception(f"向量生成失败: {e}")

    def retrieve_regulations(self, hs_code: str, product_name: str, import_country: str, export_country: str) -> list[dict]:
        """
        根据输入信息生成查询向量，并在数据库中进行余弦相似度检索
        """
        query_text = f"商品: {product_name}, HS编码: {hs_code}, 进出口国: {export_country} 到 {import_country}"
        query_vec = self.generate_embedding(query_text)
        
        # 精准检索：调用 database.py 的 search_similar_regulations
        results = database.search_similar_regulations(
            db=self.db, 
            query_embedding=query_vec, 
            top_k=3, 
            hs_code=hs_code
        )
        return results

    def generate_compliance_context(self, regulations: list[dict], product_name: str, hs_code: str) -> str:
        """
        利用 glm-4 结合检索到的法规原文生成 RAG 上下文，防幻觉
        复用项目已封装好的glm-4文本生成接口
        """
        if not regulations:
            return "未检索到匹配的海关合规政策或 RCEP 规则。"
            
        context_docs = "\n\n".join([f"法规标题: {r['title']}\n法规内容: {r['content']}" for r in regulations])
        
        prompt = f"""
        你是一个严谨的海关合规专家。请根据以下[检索到的海关政策与法规]信息，整理并总结针对当前商品的合规指导。
        
        [检索到的海关政策与法规]：
        {context_docs}
        
        [当前商品信息]：
        商品名称: {product_name}
        HS编码: {hs_code}
        
        要求：
        1. 必须仅基于上述[检索到的海关政策与法规]进行分析和总结。
        2. 如果检索到的法规与商品无关，请如实告知，绝对禁止自行编造海关政策、HS编码规则内容。
        3. 提取法规中涉及该商品的关键合规点、限制或关税减免政策。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="glm-4",
                messages=[
                    {"role": "system", "content": "你是 Z-Clear 贸易合规系统的 Sentinel Agent，必须严格基于给定的法规原文回答，禁止任何编造（防幻觉）。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"RAG 上下文生成失败: {e}")

    def execute(self, hs_code: str, product_name: str, import_country: str, export_country: str) -> dict:
        """
        Agent 核心执行入口函数
        """
        # 1. 向量检索
        regulations = self.retrieve_regulations(
            hs_code=hs_code,
            product_name=product_name,
            import_country=import_country,
            export_country=export_country
        )
        
        # 2. RAG 上下文整理
        rag_context = self.generate_compliance_context(
            regulations=regulations,
            product_name=product_name,
            hs_code=hs_code
        )
        
        # 3. 返回结构化结果
        return {
            "retrieved_regulations": regulations,
            "compliance_context": rag_context
        }
