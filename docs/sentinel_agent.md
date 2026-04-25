# Sentinel Agent 功能文档

## 1. 功能说明
Sentinel Agent 是 Z-Clear 贸易合规系统的实时政策哨兵模块。其主要职责是在单据信息提取完成后，基于 MariaDB 11.x Vector 引擎进行海关合规政策、HS 编码规则、RCEP 贸易协议的精准向量检索，随后使用大模型（glm-4）生成针对该商品的合规指导。
本模块内置了严格的 RAG（Retrieval-Augmented Generation）防幻觉机制，强制要求模型仅基于检索到的法规原文生成回答，从根源上杜绝了伪造海关政策的风险。

## 2. PRD 对齐情况
- **分支管理**：完全在 `feature/sentinel-agent` 分支进行独立开发，没有任何对 `main` 分支代码的直接破坏。
- **代码复用**：
  - 100% 复用了项目 `database.py` 已有的数据库连接与 Session 管理逻辑，通过增量追加完成了 Vector 数据库表的创建与查询。
  - 100% 复用了现有的 OpenAI API 代理方式（对接 Z.AI GLM 接口），实现了 `embedding-3` 的向量化生成和 `glm-4` 的上下文生成，没有重写任何底层大模型调用逻辑，也没有重复引入 `zhipuai` 依赖。
- **向量检索与兼容性**：
  - 使用了 MariaDB 的 `VECTOR` 类型与原生 `VEC_DISTANCE_COSINE` 余弦相似度计算，并在单元测试时提供了对 SQLite 环境的向下兼容 Fallback。
  - 单据解析、会话状态流转（RECEIVED -> EXTRACTING -> AUDITING 等）和多语言支持 100% 保持正常运行。
- **状态流转与异常处理**：
  - 在获取到合规上下文后，更新状态为 `AUDITING`，并将信息存入 `regulation_context` 字段；若过程发生报错，则更新状态为 `ERROR` 且将错误记录存入 `error_log` 字段。

## 3. 接口文档
### POST `/sentinel/retrieve`
**功能**：触发 Sentinel Agent 执行合规政策检索并返回结构化的合规指导。
**Content-Type**: `application/json`

**入参 (JSON)**:
```json
{
  "session_id": "会话的唯一ID",
  "hs_code": "海关编码 (例如: 7304)",
  "product_name": "商品名称",
  "import_country": "进口国",
  "export_country": "出口国"
}
```

**出参 (JSON) - 成功**:
```json
{
  "status": "success",
  "session_id": "会话的唯一ID",
  "regulation_context": "大模型生成的合规指导上下文...",
  "retrieved_regulations": [
    {
      "id": 1,
      "title": "法规标题",
      "content": "法规内容",
      "hs_code": "关联HS编码",
      "country": "适用国家"
    }
  ]
}
```

**出参 (JSON) - 失败**:
```json
{
  "status": "error",
  "session_id": "会话的唯一ID",
  "error_log": "异常信息详情"
}
```

## 4. 使用方法
1. 系统在调用 `/extract` 接口成功后，前端或调度模块应立即提取出解析到的 `hs_code` 和 `item_name` 等信息，调用 `POST /sentinel/retrieve` 接口。
2. Sentinel Agent 将会自动连接数据库进行政策匹配，并在匹配完成后自动更新数据库中对应 `session_id` 的状态为 `AUDITING`。
3. 数据库的升级脚本已经通过 `upgrade_db.py` 自动化实现，会自动探测 MariaDB 环境并在必要时回退到 SQLite 结构进行单元测试。

## 5. 测试结果
我们在 `tests/test_sentinel_agent.py` 补充了全流程单元测试，并经过了 `pytest` 的完整验证：
- `test_insert_and_retrieve_regulation`: 法规插入与向量检索（降级兼容）测试 —— **通过**
- `test_sentinel_agent_execute`: Agent 核心逻辑测试（Mock 大模型接口） —— **通过**
- `test_api_endpoint_success`: API 成功调用状态流转测试 —— **通过**
- `test_api_endpoint_error_handling`: API 异常捕获与状态更新（ERROR）测试 —— **通过**

所有旧有的单据提取测试（`test_extractor.py`）同样 100% 测试通过。