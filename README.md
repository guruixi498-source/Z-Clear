# Z-Clear
UMHackathon 2026 (Domain 1) | Z-Clear: A Sovereign Autonomous Trade Compliance Middleware designed to automate unstructured document auditing and reduce trade delays using Z.ai's GLM.

🎥 **Demo Video:** [https://drive.google.com/file/d/1daulKDFL0OpkRTTyUwDFxpbITLLCjyUK/view?usp=drive_link](https://drive.google.com/file/d/1daulKDFL0OpkRTTyUwDFxpbITLLCjyUK/view?usp=drive_link)

Render:https://z-clear1-0.onrender.com

---

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-teal.svg)
![AI](https://img.shields.io/badge/Powered%20by-ILMU%20GLM--5.1-orange.svg)

> **UMHackathon 2026 (Domain 1)** | A Sovereign Autonomous Trade Compliance Middleware designed to automate unstructured document auditing and reduce trade delays using Large Language Models.
>
> **马大黑客松 2026 (赛道一)** | 一款主权自主的贸易合规中间件，旨在利用大语言模型实现非结构化单据的自动化审计，并显著减少跨境贸易延迟。

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## 🌐 English Documentation

### 📌 Overview
In international trade and cross-border logistics, documents like customs declarations and commercial invoices often exist as unstructured, plain text. Traditional manual verification is inefficient, error-prone, and exacerbated by multilingual barriers.

**Z-Clear** solves this by providing a highly available, stateful middleware service. It automatically extracts core compliance data (Item Name, HS Code, Weight) from any unstructured text using the **ILMU GLM-5.1** Large Language Model and seamlessly syncs this data across a real-time **Multilingual UI** (English, Chinese, Bahasa Melayu).

### ✨ Core Features
- **Intelligent Unstructured Data Extraction**: Transforms chaotic invoice text into structured JSON data via LLM prompt engineering.
- **Robust Fallback Mechanism**: Built-in enhanced Regex parsers ensure business continuity (100% uptime) even if the external LLM API is blocked by firewalls (e.g., Cloudflare) or network timeouts.
- **Stateful Workflow Tracking**: Utilizes SQLAlchemy and SQLite to persist and track the lifecycle of each extraction request (`RECEIVED` ➔ `EXTRACTING` ➔ `AUDITING` ➔ `COMPLETED`).
- **Real-time Multilingual UI**: Dynamic status mapping allows multinational customs and logistics personnel to collaborate seamlessly in their native languages.
- **Vibe Coding**: The entire full-stack architecture was developed, refactored, and tested rapidly using **Trae AI** as an intelligent programming assistant.

### 🛠️ Tech Stack
- **Backend**: FastAPI, Uvicorn, Python 3
- **Database**: SQLite, SQLAlchemy ORM
- **AI Integration**: ILMU GLM-5.1 (via OpenAI SDK)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript

### 🚀 Getting Started (Local Development)

**1. Clone the repository & Checkout the working branch**
```bash
git clone https://github.com/guruixi498-source/Z-Clear.git
cd Z-Clear
git checkout trae/solo-agent-k8zfnw
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables**
Create a `.env` file in the root directory and add your API credentials:
```env
ILMU_API_KEY=your_api_key_here
ILMU_API_BASE=https://chat.ilmu.ai/api/v1
```

**4. Run the server**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
Then open `http://localhost:8000` in your browser.

### ☁️ Cloud Deployment (Render.com)
This project is optimized for zero-config deployment on Render:
1. Connect your GitHub repository to Render.
2. Select **Web Service**, environment: `Python 3`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add `ILMU_API_KEY` and `ILMU_API_BASE` in the Environment Variables section.

---

<a name="chinese"></a>
## 🌏 中文文档

### 📌 项目简介
在国际贸易和跨境物流中，海关报关单、商业发票等文档往往是以非结构化的纯文本形式存在的。传统的人工核对不仅效率低下、容易出错，而且在面对多国语言单据时，沟通成本呈指数级上升。

**Z-Clear** 致力于解决这一痛点。它是一个高可用的有状态中间件服务。当任意非结构化文本接入时，系统会调用 **ILMU GLM-5.1** 大语言模型，自动将其转化为标准化的合规数据（如品名、HS编码、重量），并通过其实时响应的 **多语言前端界面**（支持英文、中文、马来文），打破跨国协作的语言障碍。

### ✨ 核心特性
- **非结构化数据智能提取**：利用大模型和精确的 Prompt 工程，瞬间将杂乱无章的发票文本转化为标准的 JSON 结构。
- **高可用防崩溃兜底机制**：即使大模型 API 遭遇网络波动或遭到 Cloudflare 防火墙拦截，系统内置的增强型正则解析器也会立刻接管，确保核心业务永不中断。
- **有状态的任务工作流**：基于 SQLAlchemy 和 SQLite 实现了底层状态机，完整记录每一次请求的生命周期（`已接收` ➔ `提取中` ➔ `审计中` ➔ `处理完成`）。
- **动态多语言界面**：前后端联动的状态映射字典，允许不同国家的海关人员无缝切换语言并协同工作。
- **Vibe Coding 开发模式**：项目全程深度使用 **Trae AI** 辅助编程，极大地加速了全栈架构的设计、多文件重构以及本地终端的联调测试。

### 🛠️ 技术栈
- **后端**：FastAPI, Uvicorn, Python 3
- **数据库**：SQLite, SQLAlchemy ORM
- **AI 集成**：ILMU GLM-5.1 (基于 OpenAI SDK 兼容协议)
- **前端**：HTML5, Tailwind CSS, 原生 JavaScript

### 🚀 快速开始 (本地运行)

**1. 克隆仓库并切换到工作分支**
```bash
git clone https://github.com/guruixi498-source/Z-Clear.git
cd Z-Clear
git checkout trae/solo-agent-k8zfnw
```

**2. 安装依赖**
```bash
pip install -r requirements.txt
```

**3. 配置环境变量**
在项目根目录创建一个 `.env` 文件，填入您的 API 密钥：
```env
ILMU_API_KEY=您的_api_key
ILMU_API_BASE=https://chat.ilmu.ai/api/v1
```

**4. 启动服务器**
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
随后在浏览器中打开 `http://localhost:8000` 即可体验。

### ☁️ 云端部署 (Render.com)
本项目已针对 Render 免费云平台进行了部署优化：
1. 将 GitHub 仓库关联至 Render。
2. 创建一个 **Web Service**，运行环境选择 `Python 3`。
3. Build Command (构建命令): `pip install -r requirements.txt`
4. Start Command (启动命令): `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. 在环境变量 (Environment Variables) 选项卡中，填入 `ILMU_API_KEY` 与 `ILMU_API_BASE`。

---
*Built with ❤️ for UMHackathon 2026*
