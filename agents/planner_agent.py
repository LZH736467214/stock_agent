"""
任务规划Agent
负责解析用户查询，提取公司名称，查询股票代码
"""
import json
import re
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from .base_agent import BaseAgent
from prompts.planner import PLANNER_PROMPT
from tools.stock_search import query_stock_info


class PlannerAgent(BaseAgent):
    """任务规划Agent"""
    
    def __init__(self):
        super().__init__(
            name="任务规划Agent",
            tools=[query_stock_info],
            system_prompt=PLANNER_PROMPT
        )
    
    def run(self, state: dict) -> dict:
        """
        运行任务规划
        
        Args:
            state: 包含user_query的状态
        
        Returns:
            更新后的状态，包含company_name, stock_code, market
        """
        user_query = state.get('user_query', '')
        
        # 构建输入消息
        prompt = PLANNER_PROMPT.format(user_query=user_query)
        messages = [HumanMessage(content=prompt)]
        
        # 调用Agent
        result = self.invoke({'messages': messages})
        
        # 解析结果
        ai_message = result['messages'][-1]
        response_text = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)
        
        # 尝试从响应中提取JSON
        company_name = ""
        stock_code = ""
        market = ""
        
        try:
            # 查找JSON块
            json_match = re.search(r'\{[^{}]*"company_name"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                company_name = data.get('company_name', '')
                stock_code = data.get('stock_code', '')
                market = data.get('market', '')
        except json.JSONDecodeError:
            pass
        
        # 如果JSON解析失败，尝试从文本中提取
        if not stock_code:
            # 尝试匹配股票代码格式
            code_match = re.search(r'(sh\.\d{6}|sz\.\d{6}|hk\.\d{5})', response_text, re.IGNORECASE)
            if code_match:
                stock_code = code_match.group(1).lower()
        
        return {
            **state,
            'company_name': company_name,
            'stock_code': stock_code,
            'market': market,
            'messages': result['messages']
        }
