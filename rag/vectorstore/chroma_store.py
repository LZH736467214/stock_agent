"""
ChromaDB 向量存储封装

提供向量存储和相似度检索功能
"""
import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class ChromaVectorStore:
    """ChromaDB 向量存储"""
    
    def __init__(self, collection_name: str, persist_dir: str):
        """
        初始化 ChromaDB
        
        Args:
            collection_name: 集合名称
            persist_dir: 持久化目录
        """
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        
        # 确保目录存在
        os.makedirs(persist_dir, exist_ok=True)
        
        # 初始化客户端
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
    
    def add_documents(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        添加文档到向量库
        
        Args:
            texts: 文本内容列表
            embeddings: 向量列表
            metadatas: 元数据列表（可选）
            ids: 文档ID列表（可选，默认自动生成）
        """
        if not texts:
            return
        
        # 自动生成ID
        if ids is None:
            existing_count = self.collection.count()
            ids = [f"doc_{existing_count + i}" for i in range(len(texts))]
        
        # 默认元数据
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        print(f"    [RAG] 添加 {len(texts)} 个文档到 {self.collection_name}")
    
    def similarity_search(
        self,
        query_embedding: List[float],
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索
        
        Args:
            query_embedding: 查询向量
            k: 返回结果数量
        
        Returns:
            搜索结果列表，每个结果包含 text, metadata, distance
        """
        if self.collection.count() == 0:
            return []
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(k, self.collection.count())
        )
        
        # 格式化结果
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted_results
    
    def count(self) -> int:
        """获取文档数量"""
        return self.collection.count()
    
    def delete_collection(self) -> None:
        """删除整个集合"""
        self.client.delete_collection(self.collection_name)
        print(f"    [RAG] 已删除集合: {self.collection_name}")
    
    def clear(self) -> None:
        """清空集合内容"""
        # ChromaDB 没有直接清空的方法，需要删除后重建
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"    [RAG] 已清空集合: {self.collection_name}")
