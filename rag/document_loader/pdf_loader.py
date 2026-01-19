"""
PDF 文档加载器

解析 PDF 文件并分块
"""
import os
from typing import List, Dict, Any
from dataclasses import dataclass
from pypdf import PdfReader


@dataclass
class Document:
    """文档数据类"""
    content: str
    metadata: Dict[str, Any]


class PDFLoader:
    """PDF 文档加载器"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        初始化 PDF 加载器
        
        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 分块重叠（字符数）
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def load(self, file_path: str) -> List[Document]:
        """
        加载 PDF 文件并分块
        
        Args:
            file_path: PDF 文件路径
        
        Returns:
            文档块列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 读取 PDF
        reader = PdfReader(file_path)
        file_name = os.path.basename(file_path)
        
        documents = []
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if not text or not text.strip():
                continue
            
            # 清理文本
            text = self._clean_text(text)
            
            # 分块
            chunks = self._split_text(text)
            
            for chunk_idx, chunk in enumerate(chunks):
                if chunk.strip():
                    doc = Document(
                        content=chunk,
                        metadata={
                            'source': file_name,
                            'page': page_num,
                            'chunk': chunk_idx + 1
                        }
                    )
                    documents.append(doc)
        
        print(f"    [RAG] 加载 {file_name}: {len(reader.pages)} 页, {len(documents)} 个分块")
        return documents
    
    def load_directory(self, dir_path: str) -> List[Document]:
        """
        加载目录下所有 PDF 文件
        
        Args:
            dir_path: 目录路径
        
        Returns:
            所有文档块列表
        """
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            return []
        
        documents = []
        for file_name in os.listdir(dir_path):
            if file_name.lower().endswith('.pdf'):
                file_path = os.path.join(dir_path, file_name)
                docs = self.load(file_path)
                documents.extend(docs)
        
        return documents
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 移除多余空白
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)
    
    def _split_text(self, text: str) -> List[str]:
        """
        将文本分块
        
        使用简单的滑动窗口分块策略
        """
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # 尝试在句子边界处分割
            if end < len(text):
                # 查找最近的句子结束符
                for sep in ['。', '！', '？', '\n', '.', '!', '?']:
                    last_sep = text.rfind(sep, start, end)
                    if last_sep > start:
                        end = last_sep + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # 下一块的起始位置（考虑重叠）
            start = end - self.chunk_overlap if end < len(text) else len(text)
        
        return chunks
