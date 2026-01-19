"""
公司知识问答Agent
使用RAG检索公司内部知识库回答问题
"""
import sys
import os
from langchain_core.messages import HumanMessage
from .base_agent import BaseAgent

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.retriever.company_retriever import CompanyRetriever


class CompanyQAAgent(BaseAgent):
    """公司知识问答Agent"""
    
    SYSTEM_PROMPT = """你是一个公司内部知识助手，负责回答员工关于公司内部规章制度、流程等问题。

请根据提供的知识库内容回答问题。如果知识库中没有相关信息，请诚实告知用户。

回答要求：
1. 简洁明了，直接回答问题
2. 如果有具体流程，按步骤列出
3. 如果引用了知识库内容，说明来源
"""
    
    def __init__(self):
        super().__init__(
            name="公司知识Agent",
            tools=[],  # 不需要工具
            system_prompt=self.SYSTEM_PROMPT
        )
        self.retriever = CompanyRetriever()
    
    def run(self, state: dict) -> dict:
        """
        运行公司知识问答
        
        Args:
            state: 包含user_query的状态
        
        Returns:
            更新后的状态，包含final_report
        """
        user_query = state.get('user_query', '')
        
        # 检索相关知识
        print(f"    [CompanyQA] 检索公司知识库...")
        
        # 自动索引：如果知识库为空，尝试索引目录
        if self.retriever.count() == 0:
            print(f"    [CompanyQA] 知识库为空，正在扫描 PDF 文件...")
            count = self.retriever.index_knowledge_dir()
            print(f"    [CompanyQA] 已建立索引，共 {count} 个文档块")
            
        knowledge = self.retriever.search(user_query, k=3)
        
        if not knowledge:
            # 知识库为空
            answer = f"""## 公司知识查询
            
抱歉，公司知识库中暂无相关信息。

**您的问题**: {user_query}

当前知识库文档数: {self.retriever.count()}

请将相关文档（PDF格式）放入 `data/company_knowledge/` 目录，下次查询时会自动加载。
"""
            return {
                **state,
                'final_report': answer
            }
        
        # 构建提示
        prompt = f"""请根据以下知识库内容回答用户问题。

## 知识库内容
{knowledge}

## 用户问题
{user_query}

请给出准确、有帮助的回答："""
        
        messages = [HumanMessage(content=prompt)]
        
        try:
            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # 格式化输出
            final_report = f"""## 公司知识查询

**问题**: {user_query}

---

{answer}
"""
            return {
                **state,
                'final_report': final_report
            }
        except Exception as e:
            return {
                **state,
                'final_report': f'公司知识查询失败: {str(e)}',
                'error': str(e)
            }
