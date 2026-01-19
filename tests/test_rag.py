"""
RAG 端到端功能测试脚本

测试流程：
1. 测试 PDF 加载和分块
2. 测试 Embedding 模型
3. 测试向量存储和检索
4. 测试完整的检索器功能
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import config


def test_pdf_loader():
    """测试 PDF 加载器"""
    print("\n" + "="*50)
    print("【测试1】PDF 加载器")
    print("="*50)
    
    from rag.document_loader.pdf_loader import PDFLoader
    
    loader = PDFLoader(chunk_size=500, chunk_overlap=50)
    
    # 检查知识库目录
    knowledge_dir = config.STOCK_KNOWLEDGE_DIR
    print(f"知识库目录: {knowledge_dir}")
    
    if not os.path.exists(knowledge_dir):
        print("❌ 知识库目录不存在")
        return False
    
    pdf_files = [f for f in os.listdir(knowledge_dir) if f.endswith('.pdf')]
    print(f"PDF 文件数量: {len(pdf_files)}")
    
    if not pdf_files:
        print("❌ 没有找到 PDF 文件，请将年报放入 rag/knowledge/stock/ 目录")
        return False
    
    # 加载第一个 PDF
    pdf_path = os.path.join(knowledge_dir, pdf_files[0])
    print(f"加载文件: {pdf_files[0]}")
    
    docs = loader.load(pdf_path)
    print(f"✅ 成功加载，共 {len(docs)} 个分块")
    
    if docs:
        print(f"示例分块内容 (前200字):")
        print(f"  {docs[0].content[:200]}...")
    
    return True


def test_embedding():
    """测试 Embedding 模型"""
    print("\n" + "="*50)
    print("【测试2】Embedding 模型")
    print("="*50)
    
    from rag.embedding.qwen_embedding import QwenEmbedding
    
    embedding = QwenEmbedding()
    
    # 测试批量向量化
    texts = ["贵州茅台是中国白酒行业龙头企业", "公司主要从事白酒的生产和销售"]
    print(f"测试文本: {texts}")
    
    embeddings = embedding.embed_documents(texts)
    print(f"✅ 批量向量化成功，向量维度: {len(embeddings[0])}")
    
    # 测试查询向量化
    query = "茅台的主营业务是什么"
    query_emb = embedding.embed_query(query)
    print(f"✅ 查询向量化成功，向量维度: {len(query_emb)}")
    
    return True


def test_vectorstore():
    """测试向量存储"""
    print("\n" + "="*50)
    print("【测试3】向量存储 (ChromaDB)")
    print("="*50)
    
    from rag.vectorstore.chroma_store import ChromaVectorStore
    from rag.embedding.qwen_embedding import QwenEmbedding
    
    # 使用临时测试集合
    test_db_dir = os.path.join(config.RAG_DIR, "db", "test")
    os.makedirs(test_db_dir, exist_ok=True)
    
    store = ChromaVectorStore("test_collection", test_db_dir)
    embedding = QwenEmbedding()
    
    # 添加测试文档
    texts = [
        "贵州茅台股份有限公司是中国最大的白酒生产企业",
        "茅台酒是中国国酒，具有悠久的历史和独特的酿造工艺",
        "公司2024年营业收入达到1500亿元"
    ]
    embeddings = embedding.embed_documents(texts)
    
    store.add_documents(texts, embeddings)
    print(f"✅ 添加 {len(texts)} 条文档成功")
    print(f"当前文档数量: {store.count()}")
    
    # 测试检索
    query = "茅台的营业收入"
    query_emb = embedding.embed_query(query)
    results = store.similarity_search(query_emb, k=2)
    
    print(f"\n查询: '{query}'")
    print(f"检索结果 ({len(results)} 条):")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['text'][:50]}... (距离: {r['distance']:.4f})")
    
    # 清理测试数据
    store.clear()
    print("✅ 测试数据已清理")
    
    return True


def test_stock_retriever():
    """测试股票知识检索器"""
    print("\n" + "="*50)
    print("【测试4】股票知识检索器 (完整流程)")
    print("="*50)
    
    from rag.retriever.stock_retriever import StockRetriever
    
    retriever = StockRetriever()
    
    # 检查知识库状态
    print(f"当前向量库文档数: {retriever.count()}")
    
    # 如果为空，尝试索引知识库目录
    if retriever.count() == 0:
        print("向量库为空，开始索引知识库目录...")
        count = retriever.index_knowledge_dir()
        print(f"✅ 索引完成，添加了 {count} 个文档块")
    
    # 测试检索
    if retriever.count() > 0:
        queries = [
            "茅台的主营业务",
            "公司的财务状况",
            "风险因素"
        ]
        
        for query in queries:
            print(f"\n查询: '{query}'")
            result = retriever.search(query, k=2)
            if result:
                print(f"结果 (前300字):\n{result[:300]}...")
            else:
                print("无结果")
    else:
        print("❌ 知识库为空，请先将 PDF 放入 rag/knowledge/stock/ 目录")
        return False
    
    return True


def test_company_retriever():
    """测试公司知识检索器"""
    print("\n" + "="*50)
    print("【测试5】公司知识检索器")
    print("="*50)
    
    from rag.retriever.company_retriever import CompanyRetriever
    
    retriever = CompanyRetriever()
    
    # 添加测试文本
    test_text = """
    员工请假流程：
    1. 登录OA系统
    2. 填写请假申请单
    3. 选择请假类型（年假/事假/病假）
    4. 提交给直属领导审批
    5. 领导审批通过后生效
    """
    
    count = retriever.add_text(test_text, "员工手册")
    print(f"✅ 添加测试文档成功，{count} 个文档块")
    
    # 测试检索
    query = "如何请假"
    result = retriever.search(query, k=1)
    print(f"\n查询: '{query}'")
    print(f"结果:\n{result}")
    
    # 清理测试数据
    retriever.clear()
    print("\n✅ 测试数据已清理")
    
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("          RAG 端到端功能测试")
    print("="*60)
    
    results = {}
    
    # 测试1: PDF 加载器
    try:
        results['PDF加载器'] = test_pdf_loader()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['PDF加载器'] = False
    
    # 测试2: Embedding
    try:
        results['Embedding'] = test_embedding()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['Embedding'] = False
    
    # 测试3: 向量存储
    try:
        results['向量存储'] = test_vectorstore()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['向量存储'] = False
    
    # 测试4: 股票知识检索器
    try:
        results['股票检索器'] = test_stock_retriever()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['股票检索器'] = False
    
    # 测试5: 公司知识检索器
    try:
        results['公司检索器'] = test_company_retriever()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['公司检索器'] = False
    
    # 汇总结果
    print("\n" + "="*60)
    print("          测试结果汇总")
    print("="*60)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    print(f"\n总计: {passed_count}/{total_count} 通过\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
