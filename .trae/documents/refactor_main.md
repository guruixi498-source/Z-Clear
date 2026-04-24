# 重构 main.py 实现有状态的任务追踪与多语言支持计划

## 总结
本计划旨在重构 `main.py` 以支持多语言映射及有状态的任务追踪。我们将创建一个具有明确状态流转的提取接口，并在每个关键节点实时更新数据库中的状态。同时，我们将引入一个映射字典，根据语言环境返回不同的状态显示文本，并增加一个可通过 `session_id` 查询完整记录的 GET 接口。

## 当前状态分析
- **前端 (`static/index.html`)**：当前前端使用 `fetch('/process')`，并在本地生成一个随机的 `session_id`。
- **后端 (`main.py`)**：有一个 `@app.post("/process")` 接口，它调用 `agents/extractor.py` 中的 `process_and_store_document`。
- **数据库 (`database.py`)**：刚刚升级完毕，`SessionState` 表已包含 `status`, `raw_text`, `extracted_json`, `audit_report` 字段，且新增了 `update_session_status` 辅助函数。

## 提议的更改

### 1. 修改 `main.py` 中的提取接口
- **修改路径**：为了遵循“在 `/extract` 接口开始处”的要求，将原 `@app.post("/process")` 改为 `@app.post("/extract")`。（如果保持 `/process` 也可，但这里明确改名为 `/extract`，并随后同步更新 `index.html` 中的 fetch 路径）。
- **状态流转逻辑**：
  1. 接收到请求后，立即调用 `database.py` 创建一条新记录：
     - `session_id` = `request.session_id`
     - `status` = `"RECEIVED"`
     - `raw_text` = `request.text`
  2. 调用大模型提取前，调用 `update_session_status` 将状态更新为 `"EXTRACTING"`。
  3. 执行 `extract_info(request.text)` 提取数据。
  4. 提取成功后，将 JSON 数据存入 `extracted_json` 字段。
  5. 更新状态为 `"AUDITING"`（暂不执行实际审计）。
  6. 流程结束时，更新最终状态为 `"COMPLETED"`。
- **多语言映射**：
  - 定义 `STATUS_MAPPING` 字典，涵盖：
    - `"RECEIVED"`: `{"zh": "已接收", "en": "Received", "ms": "Diterima"}`
    - `"EXTRACTING"`: `{"zh": "提取中", "en": "Extracting", "ms": "Sedang Mengekstrak"}`
    - `"AUDITING"`: `{"zh": "审计中", "en": "Auditing", "ms": "Sedang Diaudit"}`
    - `"COMPLETED"`: `{"zh": "处理完成", "en": "Completed", "ms": "Selesai"}`
    - `"ERROR"`: `{"zh": "处理异常", "en": "Error", "ms": "Ralat"}`
  - 在返回给前端的 Response 中，加入 `display_status` 字段，其值为当前最终状态对应的多语言字典。
- **异常处理**：
  - 用 `try...except` 包裹核心提取逻辑。
  - 若报错，将状态更新为 `"ERROR"`，并将错误信息记录在数据库中（如存入 `audit_report` 或 `progress` 字段），并返回对应的响应。

### 2. 新增 GET `/session/{session_id}` 查询接口
- **路径**：`@app.get("/session/{session_id}")`
- **逻辑**：
  - 根据 `session_id` 在数据库中查找记录。
  - 如果不存在，返回 HTTP 404 Not Found。
  - 如果存在，返回完整的处理记录（包括 `raw_text`, `extracted_json`, `status` 等）以及对应的 `display_status` 多语言字典。
  - 这样如果刷新页面，前端可通过此接口获取上次的状态，从而实现断点续传。

### 3. 同步修改 `static/index.html`（兼容性保证）
- 将前端发起 fetch 请求的 URL 从 `'/process'` 改为 `'/extract'`，以匹配后端的接口名称更改。

## 假设与决策
- 假设前端继续生成并传递 `session_id`。如果需要后端生成，则前端必须进行较大改动（改为先请求 `session_id`，再轮询）。目前为了保持流程连贯，继续由前端通过 `ProcessRequest` 提供 `session_id`，后端在此 `session_id` 上进行状态跟踪和同步返回。
- 考虑到“状态实时流转”的描述，后端会在单个请求的执行过程中多次 `db.commit()`。即使这是一个同步阻塞的请求，如果在提取期间发生页面刷新，另一个请求调用 `GET /session/{session_id}` 时，依然能读取到中间状态（例如 `"EXTRACTING"`），这就满足了“有状态任务追踪”的核心诉求。

## 验证步骤
1. 重启 Uvicorn 服务器。
2. 从前端提交一次请求，观察后端日志中状态的逐步更新（RECEIVED -> EXTRACTING -> AUDITING -> COMPLETED）。
3. 检查前端能否正常显示处理结果。
4. 使用 `curl http://127.0.0.1:8000/session/<生成的session_id>`，验证新接口是否返回完整记录和 `display_status` 映射。
5. 故意输入会导致报错的参数（或切断网络），验证状态是否更新为 `ERROR` 且记录了错误信息。
