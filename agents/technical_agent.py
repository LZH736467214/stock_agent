"""
技术分析Agent
使用ReAct模式分析股票K线和价格趋势
"""
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent
from prompts.technical import TECHNICAL_PROMPT
from tools.stock_market import (
    get_historical_k_data,
    get_stock_basic_info,
    get_adjust_factor_data,
)


class TechnicalAgent(BaseAgent):
    """技术分析Agent"""
    
    def __init__(self):
        super().__init__(
            name="技术分析Agent",
            tools=[
                get_historical_k_data,
                get_stock_basic_info,
                get_adjust_factor_data,
            ],
            system_prompt=TECHNICAL_PROMPT
        )
    
    def run(self, state: dict) -> dict:
        """
        运行技术分析
        
        Args:
            state: 包含stock_code和company_name的状态
        
        Returns:
            更新后的状态，包含technical_analysis
        """
        company_name = state.get('company_name', '')
        stock_code = state.get('stock_code', '')
        
        if not stock_code:
            return {
                **state,
                'technical_analysis': '无法进行技术分析：缺少股票代码'
            }
        
        # 构建输入消息
        prompt = TECHNICAL_PROMPT.format(
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
                'technical_analysis': analysis
            }
        except Exception as e:
            return {
                **state,
                'technical_analysis': f'技术分析失败: {str(e)}'
            }
