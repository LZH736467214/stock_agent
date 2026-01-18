"""
基本面分析Agent
使用ReAct模式分析公司财务数据
"""
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent
from prompts.fundamental import FUNDAMENTAL_PROMPT
from tools.financial_reports import (
    get_profit_data,
    get_operation_data,
    get_growth_data,
    get_balance_data,
    get_cash_flow_data,
    get_dupont_data,
)


class FundamentalAgent(BaseAgent):
    """基本面分析Agent"""
    
    def __init__(self):
        super().__init__(
            name="基本面分析Agent",
            tools=[
                get_profit_data,
                get_operation_data,
                get_growth_data,
                get_balance_data,
                get_cash_flow_data,
                get_dupont_data,
            ],
            system_prompt=FUNDAMENTAL_PROMPT
        )
    
    def run(self, state: dict) -> dict:
        """
        运行基本面分析
        
        Args:
            state: 包含stock_code和company_name的状态
        
        Returns:
            更新后的状态，包含fundamental_analysis
        """
        company_name = state.get('company_name', '')
        stock_code = state.get('stock_code', '')
        
        if not stock_code:
            return {
                **state,
                'fundamental_analysis': '无法进行基本面分析：缺少股票代码'
            }
        
        # 构建输入消息
        prompt = FUNDAMENTAL_PROMPT.format(
            company_name=company_name,
            stock_code=stock_code
        )
        messages = [HumanMessage(content=prompt)]
        
        # 调用ReAct Agent
        try:
            result = self.invoke({'messages': messages})
            
            # 提取分析结果
            ai_message = result['messages'][-1]
            analysis = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)
            
            return {
                **state,
                'fundamental_analysis': analysis
            }
        except Exception as e:
            return {
                **state,
                'fundamental_analysis': f'基本面分析失败: {str(e)}'
            }
