"""
RAG (Retrieval-Augmented Generation) 模块

提供向量检索增强生成能力，支持：
- 年报/研报知识检索（股票分析增强）
- 公司内部知识检索（公司问答）
"""

from .embedding.bge_embedding import BGEEmbedding
from .vectorstore.chroma_store import ChromaVectorStore
from .retriever.stock_retriever import StockRetriever
from .retriever.company_retriever import CompanyRetriever

__all__ = [
    "BGEEmbedding",
    "ChromaVectorStore", 
    "StockRetriever",
    "CompanyRetriever",
]
