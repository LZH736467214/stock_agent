"""
股票知识检索器

用于检索年报、研报等股票相关知识
"""
import os
import sys
from typing import List, Optional

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from rag.embedding.bge_embedding import BGEEmbedding
from rag.vectorstore.chroma_store import ChromaVectorStore
from rag.document_loader.pdf_loader import PDFLoader, Document
from config import config


class StockRetriever:
    """股票知识检索器 - 用于年报/研报"""
    
    def __init__(self):
        """初始化检索器"""
        self.embedding = BGEEmbedding()
        
        # 知识库目录
        self.knowledge_dir = config.STOCK_KNOWLEDGE_DIR
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        # 向量库目录
        self.vectorstore = ChromaVectorStore("stock_knowledge", str(config.STOCK_DB_DIR))
        
        self.pdf_loader = PDFLoader(chunk_size=500, chunk_overlap=50)
    
    def add_document(self, file_path: str) -> int:
        """
        添加文档到知识库
        
        Args:
            file_path: 文件路径
        
        Returns:
            添加的文档块数量
        """
        documents = self.pdf_loader.load(file_path)
        if not documents:
            return 0
        
        # 向量化
        texts = [doc.content for doc in documents]
        embeddings = self.embedding.embed_documents(texts)
        metadatas = [doc.metadata for doc in documents]
        
        # 存储
        self.vectorstore.add_documents(texts, embeddings, metadatas)
        return len(documents)
    
    def index_knowledge_dir(self) -> int:
        """
        索引知识库目录下的所有 PDF
        
        Returns:
            总共添加的文档块数量
        """
        documents = self.pdf_loader.load_directory(str(self.knowledge_dir))
        if not documents:
            return 0
        
        # 向量化
        texts = [doc.content for doc in documents]
        embeddings = self.embedding.embed_documents(texts)
        metadatas = [doc.metadata for doc in documents]
        
        # 存储
        self.vectorstore.add_documents(texts, embeddings, metadatas)
        return len(documents)
    
    def search(self, query: str, k: int = 3) -> str:
        """
        检索相关知识
        
        Args:
            query: 查询内容
            k: 返回结果数量
        
        Returns:
            相关知识文本
        """
        if self.vectorstore.count() == 0:
            return ""
        
        # 向量化查询
        query_embedding = self.embedding.embed_query(query)
        
        # 检索
        results = self.vectorstore.similarity_search(query_embedding, k)
        
        if not results:
            return ""
        
        # 格式化结果
        formatted = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', '未知来源')
            page = result['metadata'].get('page', '?')
            formatted.append(f"【来源: {source} 第{page}页】\n{result['text']}")
        
        return "\n\n---\n\n".join(formatted)
    
    def clear(self) -> None:
        """清空知识库"""
        self.vectorstore.clear()
    
    def count(self) -> int:
        """获取文档数量"""
        return self.vectorstore.count()
