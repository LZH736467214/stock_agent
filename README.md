# 🤖 Agentic Stock Advisor | 智能股票顾问系统

基于 **LangGraph** 框架构建的企业级多 Agent 协作系统。采用"三分支"智能路由架构，集成了 **RAG（检索增强生成）** 技术，能够同时处理**股票投资分析**、**公司内部知识问答**和**通用智能对话**三种复杂场景。

---

## 🌟 核心特性

- **🧠 混合意图识别**：采用"关键词快速匹配 + LLM 语义理解"的双重机制，毫秒级路由用户意图。
- **🔄 三分支架构**：
  - **📈 股票分析**：多 Agent 并行协作（基本面/技术/估值/新闻）+ 自动提取年报信息。
  - **🏢 公司助手**：基于 RAG 检索公司内部规章制度、员工手册等 PDF 文档。
  - **💬 通用问答**：智能处理非专业领域的日常对话。
- **📚 RAG 知识增强**：
  - 自动加载 PDF 文档（年报/研报/手册）。
  - 使用 Qwen Embedding 模型进行向量化。
  - 智能提取公司+行业关键词进行精准检索。
- **🎨 现代 Web 界面**：
  - 基于 Streamlit 构建的 Apple Design 风格界面。
  - 动态进度条与实时思考日志。
  - Markdown 格式专业研报一键下载。

---

## 🏗️ 系统架构

系统采用 **LangGraph** 构建有向无环图 (DAG)，通过扇出（Fan-out）实现分析任务的并行执行，再通过扇入（Fan-in）进行汇总。

```mermaid
graph TD
    Start([👤 用户输入]) --> Planner[🧠 任务规划 Agent<br/>(混合意图识别)]
    
    Planner -->|意图: stock| Check{🔍 有股票代码?}
    Planner -->|意图: company| CompanyQA[🏢 公司知识 Agent<br/>(RAG 检索)]
    Planner -->|意图: general| GeneralQA[🤖 通用问答 Agent]
    
    %% 股票分析分支
    Check -->|是| ParallelStart((⚡ 并行开始))
    Check -->|否| GeneralQA
    
    subgraph StockAnalysis [📈 股票分析流水线]
        ParallelStart --> Fund[💰 基本面 Agent<br/>(财务/运营)]
        ParallelStart --> Tech[📉 技术面 Agent<br/>(K线/均线)]
        ParallelStart --> Val[💹 估值 Agent<br/>(PE/PB/分红)]
        ParallelStart --> News[📰 新闻 Agent<br/>(舆情/风险)]
        
        Fund --> Summarizer
        Tech --> Summarizer
        Val --> Summarizer
        News --> Summarizer
        
        RAG[(📚 股票知识库<br/>年报/研报 PDF)] -.->|提取关键词检索| Summarizer[📝 总结 Agent<br/>(生成最终报告)]
    end
    
    %% 公司知识分支
    subgraph CompanyKnowledge [🏢 公司知识库]
        Docs[(📄 内部文档 PDF)] -.->|向量化| VectorDB[(🗄️ ChromaDB)]
        VectorDB -.->|语义检索| CompanyQA
    end
    
    Summarizer --> End1([📄 投资分析报告])
    CompanyQA --> End2([💡 知识库回答])
    GeneralQA --> End3([💬 智能回复])
```

---

## 🧩 Agent 矩阵

| Agent | 核心职责 | 调用工具/模型 | 
|-------|----------|---------------|
| **Planner** | 意图分类、实体提取、任务分发 | `query_stock_info` (股票搜索) |
| **Fundamental** | 分析营收、利润、ROE、偿债能力 | `Baostock API`, `Akshare` |
| **Technical** | K线形态识别、均线系统、成交量分析 | `Baostock API` (K线数据) |
| **Valuation** | 相对估值(PE/PB)、股息率、行业对比 | `Baostock API` |
| **News** | 抓取最新新闻、进行情感评分与风险提示 | `Google/Baidu Search`, `Newspaper3k` |
| **Summarizer** | 汇总各方数据，结合 RAG 知识库生成报告 | `StockRetriever` (向量检索) |
| **CompanyQA** | 回答公司内部流程、制度等问题 | `CompanyRetriever`, `ChromaDB` |
| **GeneralQA** | 处理寒暄、百科知识等通用问题 | `LLM` (Direct) |

---

## 🚀 快速开始

### 1. 环境准备

需要 Python 3.10+ 环境。

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/stock-agent.git
cd stock-agent

# 2. 安装依赖
pip install -r requirements.txt
```

### 2. 配置密钥

复制配置文件并填入 API Key：

```bash
cp .env.example .env
```

在 `.env` 中配置：
```ini
OPENAI_API_KEY=sk-bw...  # 你的 DeepSeek/OpenAI Key
OPENAI_BASE_URL=https://api.deepseek.com  # 或其他兼容接口
OPENAI_MODEL=deepseek-chat  # 推荐使用 DeepSeek V3/R1
```

### 3. 配置 RAG 知识库（可选）

将 PDF 文件放入指定目录，系统会自动扫描建立索引：

- **股票年报/研报**：`rag/knowledge/stock/`
  - *示例：把《贵州茅台2024年报.pdf》放入此目录，报告中会自动引用年报数据。*
- **公司内部文件**：`rag/knowledge/company/`
  - *示例：把《员工手册.pdf》放入此目录，即可询问"请假流程"。*

### 4. 运行系统

#### 🖥️ 启动 Web 界面 (推荐)
```bash
streamlit run app.py
```
*访问 http://localhost:8501 体验完整功能*

#### ⌨️ 命令行交互模式
```bash
python main.py interactive
```

#### ⚡ 单次分析任务
```bash
python main.py analyze "分析贵州茅台的投资价值"
```

---

## 📂 项目结构

```
stock_agent/
├── app.py                  # Streamlit Web 前端主程序
├── main.py                 # CLI 入口程序
├── config.py               # 全局配置管理
│
├── agents/                 # Agent 核心逻辑
│   ├── planner_agent.py    # 任务规划 & 意图识别
│   ├── summarizer_agent.py # 报告生成 & RAG调用
│   ├── company_qa_agent.py # 公司知识问答
│   └── ...
│
├── graph/                  # LangGraph 工作流定义
│   ├── workflow.py         # 图结构组装 (Multi-branch Graph)
│   └── state.py            # 状态对象定义
│
├── rag/                    # RAG 检索增强模块
│   ├── db/                 # ChromaDB 向量数据库存储
│   ├── document_loader/    # PDF 文档加载器
│   ├── embedding/          # 向量模型 (Qwen)
│   ├── knowledge/          # 原始文档目录 (Stock/Company)
│   └── retriever/          # 检索器实现
│
├── tools/                  # 工具函数库
│   ├── stock_search.py     # 股票代码搜索
│   └── baostock_utils.py   # 数据接口封装
│
└── prompts/                # LLM Prompt 模板
```

---

## 📊 报告产出示例

生成的 Markdown 报告包含以下模块：

1.  **摘要 (Executive Summary)**：一句话投资建议。
2.  **基本面分析**：包含营收增长率、净利润、ROE 等核心指标解读。
3.  **技术面分析**：基于 5日/20日/60日 均线的趋势判断。
4.  **估值水位**：当前 PE-TTM 在历史分位的位置。
5.  **舆情风险**：近期新闻的情感倾向分析。
6.  **知识库洞察**：*（RAG增强）* 引用年报中关于"经营计划"或"风险提示"的原文章节。
7.  **综合评分**：1-5 星评级。

---

## ⚠️ 免责声明

本系统生成的所有分析报告仅供参考，**不构成任何投资建议**。股市有风险，入市需谨慎。开发者不对因使用本系统而产生的任何盈亏负责。

---

## License

MIT License
