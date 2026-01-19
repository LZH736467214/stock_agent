"""
Qwen Embedding 模型封装

支持:
- Qwen3-Embedding-0.6B (默认)
- 其他 sentence-transformers 兼容模型
- 本地模型路径
"""
import os
import sys
from typing import List

# 添加项目根目录
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from sentence_transformers import SentenceTransformer
from config import config


class QwenEmbedding:
    """Qwen Embedding 模型"""
    
    def __init__(self, model_path: str = None):
        """
        初始化 Embedding 模型
        
        Args:
            model_path: 模型路径，可以是:
                - HuggingFace 模型名称 (如 "Qwen/Qwen3-Embedding-0.6B")
                - 本地绝对路径 (如 "C:/models/Qwen3-Embedding-0.6B")
                - None: 使用配置中的默认模型
        """
        if model_path is None:
            # 检查本地模型目录是否存在该模型
            local_model_path = config.EMBEDDING_MODEL_DIR / "Qwen3-Embedding-0.6B"
            if local_model_path.exists():
                self.model_path = str(local_model_path)
                print(f"    [RAG] 使用本地模型: {self.model_path}")
            else:
                self.model_path = config.EMBEDDING_MODEL
                print(f"    [RAG] 使用 HuggingFace 模型: {self.model_path}")
        else:
            self.model_path = model_path
        
        self._model = None
    
    @property
    def model(self) -> SentenceTransformer:
        """延迟加载模型"""
        if self._model is None:
            print(f"    [RAG] 加载 Embedding 模型: {self.model_path}...")
            self._model = SentenceTransformer(self.model_path, trust_remote_code=True)
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
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()
