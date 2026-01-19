"""
LangGraph工作流定义
实现三分支架构：股票分析 / 公司知识 / 通用问答
"""
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END, START
from .state import StockAnalysisState
from agents import (
    PlannerAgent,
    FundamentalAgent,
    TechnicalAgent,
    ValuationAgent,
    NewsAgent,
    SummarizerAgent,
)
from agents.company_qa_agent import CompanyQAAgent


def create_planner_node():
    """创建任务规划节点"""
    _agent = None
    
    def planner_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = PlannerAgent()
        return _agent.run(state)
    
    return planner_node


def create_fundamental_node():
    """创建基本面分析节点"""
    _agent = None
    
    def fundamental_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = FundamentalAgent()
        return _agent.run(state)
    
    return fundamental_node


def create_technical_node():
    """创建技术分析节点"""
    _agent = None
    
    def technical_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = TechnicalAgent()
        return _agent.run(state)
    
    return technical_node


def create_valuation_node():
    """创建估值分析节点"""
    _agent = None
    
    def valuation_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = ValuationAgent()
        return _agent.run(state)
    
    return valuation_node


def create_news_node():
    """创建新闻分析节点"""
    _agent = None
    
    def news_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = NewsAgent()
        return _agent.run(state)
    
    return news_node


def create_summarizer_node():
    """创建总结节点"""
    _agent = None
    
    def summarizer_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = SummarizerAgent()
        return _agent.run(state)
    
    return summarizer_node


def create_company_qa_node():
    """创建公司知识问答节点"""
    _agent = None
    
    def company_qa_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _agent
        if _agent is None:
            _agent = CompanyQAAgent()
        return _agent.run(state)
    
    return company_qa_node


def create_general_qa_node():
    """创建通用问答节点"""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from config import config
    
    _llm = None
    
    def general_qa_node(state: StockAnalysisState) -> Dict[str, Any]:
        nonlocal _llm
        if _llm is None:
            _llm = ChatOpenAI(
                api_key=config.OPENAI_API_KEY,
                base_url=config.OPENAI_BASE_URL,
                model=config.OPENAI_MODEL,
                temperature=0
            )
        
        query = state.get('user_query', '')
        print(f"    [GeneralQA] 直接 LLM 回答: {query}")
        
        messages = [HumanMessage(content=query)]
        response = _llm.invoke(messages)
        answer = response.content if hasattr(response, 'content') else str(response)
        
        return {
            **state,
            'final_report': f"## 问答\n\n**问题**: {query}\n\n**回答**: {answer}"
        }
    
    return general_qa_node


def route_by_intent(state: StockAnalysisState) -> str:
    """
    根据意图路由到对应分支
    
    Returns:
        'stock': 股票分析分支
        'company': 公司知识分支
        'general': 通用问答分支
    """
    intent = state.get('intent', 'stock')
    print(f"    [Router] 路由到: {intent}")
    return intent


def should_continue_stock(state: StockAnalysisState) -> str:
    """判断股票分析是否继续"""
    if state.get('stock_code'):
        return "continue"
    return "end"


def create_stock_analysis_graph():
    """
    创建股票分析工作流图 (旧版本，仅支持股票分析)
    """
    # 创建状态图
    workflow = StateGraph(StockAnalysisState)
    
    # 添加节点
    workflow.add_node("planner", create_planner_node())
    workflow.add_node("fundamental", create_fundamental_node())
    workflow.add_node("technical", create_technical_node())
    workflow.add_node("valuation", create_valuation_node())
    workflow.add_node("news", create_news_node())
    workflow.add_node("summarizer", create_summarizer_node())
    
    # 设置入口节点
    workflow.set_entry_point("planner")
    
    # 添加条件边：任务规划后判断是否继续
    workflow.add_conditional_edges(
        "planner",
        should_continue_stock,
        {
            "continue": "fundamental",
            "end": END
        }
    )
    
    workflow.add_edge("fundamental", "summarizer")
    workflow.add_edge("technical", "summarizer") 
    workflow.add_edge("valuation", "summarizer")
    workflow.add_edge("news", "summarizer")
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()


def create_stock_analysis_graph_v2():
    """
    创建股票分析工作流图 (并行版本)
    
    使用扇出-扇入模式实现四个分析节点并行执行
    """
    from langgraph.constants import Send
    
    workflow = StateGraph(StockAnalysisState)
    
    # 添加节点
    workflow.add_node("planner", create_planner_node())
    workflow.add_node("fundamental", create_fundamental_node())
    workflow.add_node("technical", create_technical_node())
    workflow.add_node("valuation", create_valuation_node())
    workflow.add_node("news", create_news_node())
    workflow.add_node("summarizer", create_summarizer_node())
    
    workflow.set_entry_point("planner")
    
    def fan_out_to_analyzers(state: StockAnalysisState) -> List[Send]:
        if state.get('stock_code'):
            return [
                Send("fundamental", state),
                Send("technical", state),
                Send("valuation", state),
                Send("news", state),
            ]
        return []
    
    workflow.add_conditional_edges(
        "planner",
        fan_out_to_analyzers,
        ["fundamental", "technical", "valuation", "news"]
    )
    
    workflow.add_edge("fundamental", "summarizer")
    workflow.add_edge("technical", "summarizer")
    workflow.add_edge("valuation", "summarizer")
    workflow.add_edge("news", "summarizer")
    workflow.add_edge("summarizer", END)
    
    return workflow.compile()


def create_multi_branch_graph():
    """
    创建三分支工作流图 (RAG版本)
    
    架构：
    planner（意图识别）
        ├── stock: [fundamental, technical, valuation, news] -> summarizer
        ├── company: company_qa
        └── general: general_qa
    """
    from langgraph.constants import Send
    
    workflow = StateGraph(StockAnalysisState)
    
    # 添加所有节点
    workflow.add_node("planner", create_planner_node())
    workflow.add_node("fundamental", create_fundamental_node())
    workflow.add_node("technical", create_technical_node())
    workflow.add_node("valuation", create_valuation_node())
    workflow.add_node("news", create_news_node())
    workflow.add_node("summarizer", create_summarizer_node())
    workflow.add_node("company_qa", create_company_qa_node())
    workflow.add_node("general_qa", create_general_qa_node())
    
    workflow.set_entry_point("planner")
    
    # 三分支路由
    def route_after_planner(state: StockAnalysisState):
        intent = state.get('intent', 'stock')
        
        if intent == 'company':
            return 'company'
        elif intent == 'general':
            return 'general'
        else:
            # 股票分析：检查是否有股票代码
            if state.get('stock_code'):
                return 'stock'
            else:
                return 'end'
    
    workflow.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "stock": "fundamental",
            "company": "company_qa",
            "general": "general_qa",
            "end": END
        }
    )
    
    # 股票分析流程
    workflow.add_edge("fundamental", "technical")
    workflow.add_edge("technical", "valuation")
    workflow.add_edge("valuation", "news")
    workflow.add_edge("news", "summarizer")
    workflow.add_edge("summarizer", END)
    
    # 公司知识和通用问答直接结束
    workflow.add_edge("company_qa", END)
    workflow.add_edge("general_qa", END)
    
    return workflow.compile()
