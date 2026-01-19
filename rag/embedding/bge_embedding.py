"""
BGE Embedding 模型封装

使用 BAAI/bge-small-zh-v1.5 进行中文文本向量化
"""
from typing import List
from sentence_transformers import SentenceTransformer


class BGEEmbedding:
    """BGE 中文 Embedding 模型"""
    
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """
        初始化 BGE Embedding 模型
        
        Args:
            model_name: 模型名称，默认使用 bge-small-zh
        """
        self.model_name = model_name
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """延迟加载模型"""
        if self._model is None:
            print(f"    [RAG] 加载 Embedding 模型: {self.model_name}...")
            self._model = SentenceTransformer(self.model_name)
            print(f"    [RAG] Embedding 模型加载完成")
        return self._model
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量文本向量化
        
        Args:
            texts: 文本列表
        
        Returns:
            向量列表
        """
        if not texts:
            return []
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """
        单条查询文本向量化
        
        Args:
            text: 查询文本
        
        Returns:
            向量
        """
        # BGE 模型查询时需要加前缀以获得更好效果
        query_text = f"为这个句子生成表示以用于检索相关文章：{text}"
        embedding = self.model.encode(query_text, normalize_embeddings=True)
        return embedding.tolist()
