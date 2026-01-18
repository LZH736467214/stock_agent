"""
新闻分析Agent
使用ReAct模式爬取新闻并进行情感/风险分析
"""
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent
from prompts.news import NEWS_PROMPT
from tools.news_crawler import crawl_news


class NewsAgent(BaseAgent):
    """新闻分析Agent"""
    
    def __init__(self):
        super().__init__(
            name="新闻分析Agent",
            tools=[crawl_news],
            system_prompt=NEWS_PROMPT
        )
    
    def run(self, state: dict) -> dict:
        """
        运行新闻分析
        
        Args:
            state: 包含company_name的状态
        
        Returns:
            更新后的状态，包含news_analysis
        """
        company_name = state.get('company_name', '')
        stock_code = state.get('stock_code', '')
        
        if not company_name:
            return {
                **state,
                'news_analysis': '无法进行新闻分析：缺少公司名称'
            }
        
        # 构建输入消息
        prompt = NEWS_PROMPT.format(
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
                'news_analysis': analysis
            }
        except Exception as e:
            return {
                **state,
                'news_analysis': f'新闻分析失败: {str(e)}'
            }
