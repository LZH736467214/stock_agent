"""
LangGraph状态定义
"""
from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages


class StockAnalysisState(TypedDict):
    """股票分析状态定义"""
    
    # 用户输入
    user_query: str
    
    # 意图识别结果
    intent: str  # "stock" | "company" | "general"
    
    # 任务规划结果
    company_name: str
    stock_code: str
    market: str  # A股-上海/A股-深圳/港股/美股
    
    # 各Agent分析结果
    fundamental_analysis: Optional[str]
    technical_analysis: Optional[str]
    valuation_analysis: Optional[str]
    news_analysis: Optional[str]
    
    # 最终报告
    final_report: Optional[str]
    
    # 错误信息
    error: Optional[str]
    
    # 消息历史 (用于ReAct Agent)
    messages: Annotated[List, add_messages]
