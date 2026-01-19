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
    
    def _extract_industry_from_text(self, text: str) -> str:
        """
        使用 LLM 从文本中提取行业信息
        
        Args:
            text: 分析文本
        
        Returns:
            行业名称
        """
        if not text or text == '暂无数据':
            return ""
        
        prompt = f"""从以下分析文本中提取公司所属行业，只返回行业名称（如：白酒、新能源、医药、银行、房地产）。
如果无法确定行业，返回空字符串。

分析文本：
{text[:800]}

行业名称："""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            industry = response.content.strip()[:20]  # 限制长度
            # 清理可能的多余内容
            industry = industry.split('\n')[0].strip()
            return industry
        except Exception as e:
            print(f"    [Summarizer] 行业提取失败: {e}")
            return ""
    
    def _extract_company_and_industry(self, state: dict) -> tuple:
        """
        从 state 和前序分析中提取公司名称和行业
        
        Args:
            state: 工作流状态
        
        Returns:
            (company_name, industry) 元组
        """
        # 1. 公司名称：优先从 state 获取
        company_name = state.get('company_name', '')
        
        # 2. 行业：从基本面分析中提取
        fundamental = state.get('fundamental_analysis', '')
        industry = self._extract_industry_from_text(fundamental)
        
        # 如果基本面没有行业信息，尝试从估值分析提取
        if not industry:
            valuation = state.get('valuation_analysis', '')
            industry = self._extract_industry_from_text(valuation)
        
        print(f"    [Summarizer] 提取结果 - 公司: {company_name}, 行业: {industry or '未知'}")
        return company_name, industry
    
    def _get_knowledge_context(self, company_name: str, industry: str = "") -> str:
        """
        从知识库检索相关内容
        
        Args:
            company_name: 公司名称
            industry: 所属行业
        
        Returns:
            知识库内容
        """
        if self.retriever.count() == 0:
            print(f"    [Summarizer] 知识库为空，跳过RAG检索")
            return ""
        
        # 仅使用公司名称和行业进行精准检索
        query_parts = [company_name]
        if industry:
            query_parts.append(industry)
        query = ' '.join(query_parts)
        
        print(f"    [Summarizer] RAG检索查询: {query}")
        
        knowledge = self.retriever.search(query, k=3)
        if knowledge:
            print(f"    [Summarizer] ✅ 找到 {len(knowledge.split('---'))} 条相关知识")
        else:
            print(f"    [Summarizer] ⚠️  知识库无匹配内容")
        
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
        
        # RAG 增强：智能提取公司和行业，精准检索
        extracted_company, industry = self._extract_company_and_industry(state)
        knowledge_context = self._get_knowledge_context(
            extracted_company or company_name, 
            industry
        )
        
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
