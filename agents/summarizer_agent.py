"""
总结Agent
汇总所有分析结果，生成完整的投资分析报告
"""
from datetime import datetime
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent
from prompts.summarizer import SUMMARIZER_PROMPT


class SummarizerAgent(BaseAgent):
    """总结Agent"""
    
    def __init__(self):
        super().__init__(
            name="总结Agent",
            tools=[],  # 不需要工具，纯LLM生成
            system_prompt=SUMMARIZER_PROMPT
        )
    
    def run(self, state: dict) -> dict:
        """
        运行总结生成
        
        Args:
            state: 包含所有分析结果的状态
        
        Returns:
            更新后的状态，包含final_report
        """
        company_name = state.get('company_name', '未知公司')
        stock_code = state.get('stock_code', '未知代码')
        market = state.get('market', '未知市场')
        
        fundamental_analysis = state.get('fundamental_analysis', '暂无数据')
        technical_analysis = state.get('technical_analysis', '暂无数据')
        valuation_analysis = state.get('valuation_analysis', '暂无数据')
        news_analysis = state.get('news_analysis', '暂无数据')
        
        # 构建输入消息
        prompt = SUMMARIZER_PROMPT.format(
            company_name=company_name,
            stock_code=stock_code,
            market=market,
            fundamental_analysis=fundamental_analysis,
            technical_analysis=technical_analysis,
            valuation_analysis=valuation_analysis,
            news_analysis=news_analysis
        )
        messages = [HumanMessage(content=prompt)]
        
        # 调用LLM生成报告
        try:
            response = self.llm.invoke(messages)
            report = response.content if hasattr(response, 'content') else str(response)
            
            # 添加报告头和时间戳
            final_report = f"""# {company_name} ({stock_code}) 投资分析报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **市场**: {market}

---

{report}
"""
            
            return {
                **state,
                'final_report': final_report
            }
        except Exception as e:
            return {
                **state,
                'final_report': f'报告生成失败: {str(e)}',
                'error': str(e)
            }
