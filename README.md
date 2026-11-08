<div align="center">

# 🧠 Autonomous Research Agent

### Single-agent research engine powered by **LangGraph**, **Google Gemini**, and **Tavily Search** with **Multi-Model Fault Tolerance**.

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph%201.2+-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Google Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![Tavily](https://img.shields.io/badge/Search-Tavily%20AI-00C7B7?style=for-the-badge&logo=search&logoColor=white)](https://tavily.com/)
[![Docker](https://img.shields.io/badge/Container-Docker%20Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

<br />

<p align="center">
  <a href="#-architecture--workflow">Architecture</a> •
  <a href="#-key-features">Key Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-docker-deployment">Docker</a> •
  <a href="#-environment-variables">Configuration</a> •
  <a href="#-sample-reports">Sample Reports</a>
</p>

</div>

---

## 📌 Overview

The **Autonomous Research Agent** is a dedicated single-agent research engine designed to investigate topics, synthesize findings across real-time web search and verified encyclopedia knowledge bases, and automatically compile structured, executive-grade Markdown reports.

Unlike fragile linear LLM prompt chains, this agent runs on a **cyclic LangGraph state machine** equipped with **Multi-Model Fallback Failover**—automatically circumventing Google Free-Tier rate limits (`429 RESOURCE_EXHAUSTED` and `503 UNAVAILABLE`) in real time.

---

## 🏛 Architecture & Workflow

### End-to-End System Flowchart

<div align="center">
  <img src="assets/architecture-diagram.svg" alt="Autonomous Research Agent Architecture Flow" width="900"/>
</div>

### Interactive State Graph

```mermaid
flowchart TD
    START([🚀 START: Research Topic]) --> AgentNode[🧠 Agent Node<br/>Gemini Model Chain]
    
    AgentNode --> Decision{🛠️ Tool Call<br/>Requested?}
    
    Decision -- Yes --> ToolNode[⚡ Tool Execution Node]
    
    subgraph Tools [Available Agent Capabilities]
        Tool1["📅 get_current_date()"]
        Tool2["🌐 tavily_search()"]
        Tool3["📚 wikipedia()"]
        Tool4["💾 save_report()"]
    end
    
    ToolNode --> Tools
    Tools --> AgentNode
    
    Decision -- No / Finished --> SaveReport[📄 Markdown Report Saved<br/>reports/*.md]
    SaveReport --> END([🏁 Complete])

    style AgentNode fill:#1e293b,stroke:#38bdf8,stroke-width:2px,color:#fff
    style ToolNode fill:#1e293b,stroke:#a855f7,stroke-width:2px,color:#fff
    style Decision fill:#0f172a,stroke:#f59e0b,stroke-width:2px,color:#fff
    style Tools fill:#0f172a,stroke:#334155,stroke-width:1px,color:#fff
    style START fill:#047857,color:#fff
    style END fill:#1d4ed8,color:#fff
```

### Resilient Multi-Model Failover Architecture

Free-tier LLM APIs impose strict daily token and request limits. To guarantee 99.9% task completion without manual intervention, the agent uses LangChain's `with_fallbacks` architecture:

```mermaid
graph LR
    Req[LLM Request] --> M1[gemini-3.5-flash-lite]
    M1 -- "429 / 503 error" --> M2[gemini-3-flash-preview]
    M2 -- "429 / 503 error" --> M3[gemini-3.8-flash]
    M3 -- "429 / 503 error" --> M4[gemini-3.5-flash]
    
    M1 -->|Success| Response([Processed Output])
    M2 -->|Success| Response
    M3 -->|Success| Response
    M4 -->|Success| Response

    style Req fill:#0284c7,color:#fff
    style Response fill:#16a34a,color:#fff
    style M1 fill:#1e293b,stroke:#38bdf8,color:#fff
    style M2 fill:#1e293b,stroke:#f59e0b,color:#fff
    style M3 fill:#1e293b,stroke:#ec4899,color:#fff
    style M4 fill:#1e293b,stroke:#8b5cf6,color:#fff
```

---

## ✨ Key Features

| Capability | Description |
| :--- | :--- |
| **🔄 Cyclical LangGraph Graph** | Implements standard state reduction (`add_messages`), checkpoint memory (`MemorySaver`), and self-correcting loops until research goals are met. |
| **🛡️ Zero-Downtime Model Fallbacks** | Cascades through 4+ Gemini Flash variants on `429` (Quota Exhausted) or `503` (High Demand) within 3 seconds. |
| **🔍 Multi-Vector Sourcing** | Combines real-time web grounding via **Tavily AI Search** with deep background verification via **Wikipedia API**. |
| **📅 Temporal Anchoring** | Automatically verifies current system date before querying so the agent distinguishes historical records from recent breakthroughs. |
| **📊 Structured Markdown Exporter** | Synthesizes findings into comprehensive Markdown files containing Executive Summaries, Key Findings, Comparative Tables, and Verified Citations. |
| **🐳 Containerized & Cloud-Ready** | Pre-configured `Dockerfile` and `docker-compose.yml` with persistent host volume mounts for instant reproduction. |

---

## 📂 Project Structure

```text
research-agent/
├── .env.example                     # Environment template with API instructions
├── .gitignore                       # Production Git rules (protects keys & environments)
├── .dockerignore                    # Build optimization rules for Docker
├── Dockerfile                       # Multi-stage container recipe
├── docker-compose.yml               # Single-command orchestration with volume mounts
├── requirements.txt                 # Exact, verified Python dependencies
├── main.py                          # Core LangGraph agent & tool definitions
├── assets/
│   ├── architecture-diagram.svg     # High-resolution vector flowchart
│   └── architecture-diagram.pdf     # Vector PDF schematic
└── reports/                         # Destination directory for generated research
    ├── .gitkeep                     # Preserves directory in git
    └── state_of_ai_agents_2026.md   # Sample research report generated by agent
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (Tested up to Python 3.14) or Docker
- [Google Gemini API Key](https://aistudio.google.com/app/apikey) (Free)
- [Tavily Search API Key](https://tavily.com) (Free tier includes 1,000 monthly queries)

### 2. Local Installation

```bash
# 1. Clone your repository
git clone https://github.com/your-username/research-agent.git
cd research-agent

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your environment variables
cp .env.example .env
```

Open `.env` and paste your keys:
```env
GOOGLE_API_KEY="AIzaSy..."
TAVILY_API_KEY="tvly-..."
```

### 3. Run the Agent

Run with the default topic:
```bash
python main.py
```

Or pass any custom research query directly via CLI:
```bash
python main.py "Breakthroughs in Solid-State Batteries in 2026"
```

The completed report will be saved automatically into the `reports/` folder.

---

## 🐳 Docker Deployment

The application is fully containerized. Reports generated inside the container are mounted directly to your local `./reports/` directory.

### Using Docker Compose (Recommended)

1. Make sure your `.env` file is configured:
   ```bash
   cp .env.example .env
   ```

2. Run with default topic:
   ```bash
   docker compose run --rm research-agent
   ```

3. Run with a custom topic:
   ```bash
   docker compose run --rm research-agent "Quantum Computing Roadmap 2026"
   ```

### Using Plain Docker CLI

```bash
# Build the image
docker build -t research-agent .

# Run with environment and mounted reports folder
docker run --rm \
  --env-file .env \
  -v $(pwd)/reports:/app/reports \
  research-agent "Global Semiconductor Supply Chain 2026"
```

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `GOOGLE_API_KEY` | **Yes** | — | Google AI Studio API key used for Gemini reasoning models. |
| `TAVILY_API_KEY` | **Yes** | — | Tavily Search API key used for real-time web querying. |
| `GEMINI_MODEL` | No | `gemini-3.5-flash-lite` | Preferred starting model before triggering fallback chain. |

---

## 📝 Sample Report Output

Each generated report is saved as an individual Markdown document formatted with standard sections:

```markdown
# Comprehensive Report: Current State of AI Agents in 2026

## Executive Summary
Over 40% of enterprise software applications embed task-specific AI agents...

## Key Findings
- 57% of deploying enterprises use multi-agent systems (MAS) rather than monolithic prompts.
- Model Context Protocol (MCP) standardized tool connectivity across major providers.
...

## Detailed Analysis
[Detailed thematic breakdowns, metrics, and architecture comparisons]

## Sources
- [Gate AI: Agent Model Benchmarks 2026](https://gate.ai/...)
- [Google Cloud Agentic Enterprise Study](https://cloud.google.com/...)
```

See [reports/state_of_ai_agents_2026.md](reports/state_of_ai_agents_2026.md) for a full example.

---

## 📤 Pushing to GitHub

To publish this repository to your GitHub account:

```bash
# 1. Initialize Git (if not already done)
git init -b main

# 2. Stage all project files (verifying .env and .venv are ignored)
git add .

# 3. Check staged files
git status

# 4. Make initial commit
git commit -m "feat: initial commit of autonomous research agent"

# 5. Link to your GitHub repository
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 6. Push to main branch
git push -u origin main
```

---

## 📜 License

This project is open-source and licensed under the [MIT License](LICENSE).
