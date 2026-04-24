# Tasks
- [x] Task 1: 升级数据库表结构：在 `database.py` 中修改 `SessionState` 类，添加 `raw_text`, `extracted_json`, `audit_report` 字段，并更新 `status` 字段以匹配新状态集（'RECEIVED', 'EXTRACTING', 'AUDITING', 'PENDING_REMEDY', 'COMPLETED'）。
- [x] Task 2: 添加状态更新函数：在 `database.py` 中实现 `update_session_status(db, session_id, status)` 逻辑，支持根据 `session_id` 查找并更新状态。
- [x] Task 3: 确保在不修改 `main.py` 的前提下，修改完 `database.py` 后代码无语法错误。

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
