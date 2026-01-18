"""
估值分析Agent
使用ReAct模式分析公司估值和行业对比
"""
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent
from prompts.valuation import VALUATION_PROMPT
from tools.stock_market import get_stock_basic_info, get_dividend_data
from tools.indices import get_stock_industry, get_hs300_stocks
from tools.financial_reports import get_profit_data


class ValuationAgent(BaseAgent):
    """估值分析Agent"""
    
    def __init__(self):
        super().__init__(
            name="估值分析Agent",
            tools=[
                get_stock_basic_info,
                get_dividend_data,
                get_stock_industry,
                get_hs300_stocks,
                get_profit_data,
            ],
            system_prompt=VALUATION_PROMPT
        )
    
    def run(self, state: dict) -> dict:
        """
        运行估值分析
        
        Args:
            state: 包含stock_code和company_name的状态
        
        Returns:
            更新后的状态，包含valuation_analysis
        """
        company_name = state.get('company_name', '')
        stock_code = state.get('stock_code', '')
        
        if not stock_code:
            return {'valuation_analysis': '无法进行估值分析：缺少股票代码'}
        
        # 构建输入消息
        prompt = VALUATION_PROMPT.format(
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
            
            return {'valuation_analysis': analysis}
        except Exception as e:
            return {'valuation_analysis': f'估值分析失败: {str(e)}'}
