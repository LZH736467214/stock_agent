"""
LangGraph工作流定义
实现"总-分-总"架构的股票分析流程
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import StockAnalysisState
from agents import (
    PlannerAgent,
    FundamentalAgent,
    TechnicalAgent,
    ValuationAgent,
    NewsAgent,
    SummarizerAgent,
)


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


def should_continue(state: StockAnalysisState) -> str:
    """
    路由函数：判断是否继续执行分析
    
    如果任务规划成功（有股票代码），则继续执行分析
    否则直接结束
    """
    if state.get('stock_code'):
        return "continue"
    return "end"


def create_stock_analysis_graph():
    """
    创建股票分析工作流图
    
    架构：总-分-总
    1. 任务规划 (总)
    2. 四个并行分析 (分): 基本面、技术面、估值、新闻
    3. 总结报告 (总)
    
    Returns:
        编译后的工作流图
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
        should_continue,
        {
            "continue": "fundamental",  # 继续执行分析
            "end": END  # 结束
        }
    )
    
    # 添加并行执行的边
    # 注意：LangGraph默认是顺序执行，这里我们通过添加多个边来表示依赖关系
    # 四个分析节点都依赖planner，但互不依赖，可以并行
    workflow.add_edge("fundamental", "summarizer")
    workflow.add_edge("technical", "summarizer") 
    workflow.add_edge("valuation", "summarizer")
    workflow.add_edge("news", "summarizer")
    
    # 由于上面的设置会导致summarizer被调用4次，我们需要修改架构
    # 使用扇出-扇入模式
    
    # 重新设计：使用并行分支
    # planner -> [fundamental, technical, valuation, news] -> summarizer
    
    # 总结节点到结束
    workflow.add_edge("summarizer", END)
    
    # 编译图
    return workflow.compile()


def create_stock_analysis_graph_v2():
    """
    创建股票分析工作流图 (改进版本)
    
    使用顺序执行确保状态正确传递
    
    架构：
    planner -> fundamental -> technical -> valuation -> news -> summarizer
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
        should_continue,
        {
            "continue": "fundamental",
            "end": END
        }
    )
    
    # 顺序执行各分析节点
    workflow.add_edge("fundamental", "technical")
    workflow.add_edge("technical", "valuation")
    workflow.add_edge("valuation", "news")
    workflow.add_edge("news", "summarizer")
    workflow.add_edge("summarizer", END)
    
    # 编译图
    return workflow.compile()
