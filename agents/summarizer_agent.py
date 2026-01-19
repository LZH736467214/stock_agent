"""
总结Agent
汇总所有分析结果，生成完整的投资分析报告
支持 RAG 增强：从年报/研报知识库检索相关内容
"""
import sys
import os
from datetime import datetime
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent
from prompts.summarizer import SUMMARIZER_PROMPT

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.retriever.stock_retriever import StockRetriever


class SummarizerAgent(BaseAgent):
    """总结Agent - 支持 RAG 增强"""
    
    def __init__(self):
        super().__init__(
            name="总结Agent",
            tools=[],  # 不需要工具，纯LLM生成
            system_prompt=SUMMARIZER_PROMPT
        )
        # 初始化 RAG 检索器
        self._retriever = None
    
    @property
    def retriever(self) -> StockRetriever:
        """延迟加载检索器"""
        if self._retriever is None:
            self._retriever = StockRetriever()
        return self._retriever
    
    def _get_knowledge_context(self, company_name: str) -> str:
        """
        从知识库检索相关内容
        
        Args:
            company_name: 公司名称
        
        Returns:
            知识库内容
        """
        if self.retriever.count() == 0:
            return ""
        
        # 构建查询
        query = f"{company_name} 业务 财务 风险 发展"
        print(f"    [Summarizer] 检索知识库: {query}")
        
        knowledge = self.retriever.search(query, k=3)
        if knowledge:
            print(f"    [Summarizer] 找到 {len(knowledge.split('---'))} 条相关知识")
        else:
            print(f"    [Summarizer] 知识库无相关内容")
        
        return knowledge
    
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
        
        # RAG 增强：检索知识库
        knowledge_context = self._get_knowledge_context(company_name)
        
        # 构建输入消息
        prompt = SUMMARIZER_PROMPT.format(
            company_name=company_name,
            stock_code=stock_code,
            market=market,
            fundamental_analysis=fundamental_analysis,
            technical_analysis=technical_analysis,
            valuation_analysis=valuation_analysis,
            news_analysis=news_analysis,
            knowledge_context=knowledge_context if knowledge_context else "无相关知识库内容"
        )
        messages = [HumanMessage(content=prompt)]
        
        # 调用LLM生成报告
        try:
            response = self.llm.invoke(messages)
            report = response.content if hasattr(response, 'content') else str(response)
            
            # 添加报告头和时间戳
            rag_note = "\n> **知识库**: 已参考年报/研报内容" if knowledge_context else ""
            final_report = f"""# {company_name} ({stock_code}) 投资分析报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **市场**: {market}{rag_note}

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
