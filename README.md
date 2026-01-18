# 多Agent股票顾问系统

基于 **LangGraph** 框架构建的多Agent股票分析系统，采用"总-分-总"架构，支持A股、港股分析。

## 系统架构

```
用户输入 → 任务规划Agent → [基本面/技术面/估值/新闻 Agent (并行)] → 总结Agent → Markdown报告
```

### Agent职责

| Agent | 职责 | 工具 |
|-------|------|------|
| 任务规划 | 提取公司名称，查询股票代码 | `query_stock_info` |
| 基本面分析 | 分析盈利、成长、运营、偿债能力 | 财务报表工具 |
| 技术分析 | 分析K线趋势、成交量 | K线数据工具 |
| 估值分析 | 估值对比、行业分析 | 估值工具 |
| 新闻分析 | 情感/风险评分 | 新闻爬取工具 |
| 总结 | 生成Markdown报告 | - |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入 OPENAI_API_KEY
```

### 3. 运行分析

```bash
# 单次分析
python main.py analyze "分析贵州茅台的投资价值"

# 交互模式
python main.py interactive

# 5. 启动Web界面
streamlit run app.py

# 查看帮助
python main.py --help
```

## 项目结构

```
stock_agent/
├── main.py              # 入口文件
├── config.py            # 配置管理
├── tools/               # MCP工具层
│   ├── stock_market.py  # 股票市场数据
│   ├── financial_reports.py  # 财务报表
│   ├── news_crawler.py  # 新闻爬取
│   └── ...
├── agents/              # Agent层
│   ├── planner_agent.py
│   ├── fundamental_agent.py
│   ├── technical_agent.py
│   ├── valuation_agent.py
│   ├── news_agent.py
│   └── summarizer_agent.py
├── graph/               # LangGraph工作流
│   ├── state.py         # 状态定义
│   └── workflow.py      # 图结构
├── prompts/             # Prompt模板
└── output/              # 报告输出
```

## 报告示例

生成的报告包含10个部分：
1. 摘要
2. 公司概况
3. 基本面分析
4. 技术分析
5. 估值分析
6. 新闻分析
7. 综合评估
8. 风险因素
9. 投资建议
10. 附录

## 注意事项

- 需要配置 `OPENAI_API_KEY`
- 股票数据来源于 Baostock (仅支持A股)
- 新闻爬取使用百度搜索
- 本系统仅供参考，不构成投资建议

## License

MIT
