# Upgrade Database State Spec

## Why
Z-Clear 核心架构需要符合“有状态代理工作流”的要求。当前的数据库结构缺乏足够的细粒度字段，无法满足多阶段处理（如接收、提取、审计、需补全、已完成）的状态跟踪以及断点续传的需求。

## What Changes
- 修改 `database.py` 中现有的 `SessionState` 表结构（为了保持现有代码兼容性，我们直接扩展它而不是重命名表名）。
- 为表添加以下新字段：
  - `status`: 字符串类型，用于记录当前状态（例如：'RECEIVED', 'EXTRACTING', 'AUDITING', 'PENDING_REMEDY', 'COMPLETED'）
  - `raw_text`: 文本类型，存储原始单据文本
  - `extracted_json`: 文本类型（存储JSON字符串），存储提取出的结构化数据
  - `audit_report`: 文本类型（存储JSON字符串），存储审计报告
- 在 `database.py` 中添加一个辅助函数 `update_session_status(db, session_id, status)`，用于根据 `session_id` 快速更新状态。
- 确保数据库的初始化逻辑可以正常运行。
- **BREAKING**: 由于 SQLite 不支持通过原生的方式轻松删除或大改列，如果是已有的本地数据库，可能需要手动删除 `zclear.db` 或重新初始化（由于是新开发阶段，我们将直接在代码中通过 `create_all` 确保新库的建立，具体根据实际情况）。但绝不修改 `main.py`。

## Impact
- Affected specs: 数据库持久化存储与多语言状态追踪能力
- Affected code: `database.py`

## ADDED Requirements
### Requirement: 状态追踪与数据留存
系统 SHALL 提供保存各个处理阶段数据以及状态的功能。

#### Scenario: 成功更新状态
- **WHEN** 调用 `update_session_status` 传递新的状态值
- **THEN** 数据库中对应 `session_id` 的记录的 `status` 字段更新为指定状态，并持久化到 SQLite 数据库中。
