"""
三分支路由和 RAG 集成测试

测试内容：
1. Planner 能否准确识别三种意图（stock / company / general）
2. RAG 是否集成到 Summarizer 中
3. 端到端工作流测试
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import config


def test_intent_classification():
    """测试1: PlannerAgent 意图识别"""
    print("\n" + "="*60)
    print("【测试1】PlannerAgent 意图识别")
    print("="*60)
    
    from agents.planner_agent import PlannerAgent
    
    planner = PlannerAgent()
    
    # 测试用例：股票、公司、通用
    test_cases = [
        ("分析贵州茅台的投资价值", "stock"),
        ("茅台的股价走势如何", "stock"),
        ("五粮液的财报怎么样", "stock"),
        ("公司请假流程是什么", "company"),
        ("员工手册在哪里找", "company"),
        ("如何报销差旅费", "company"),
        ("今天天气怎么样", "general"),
        ("Python如何写循环", "general"),
        ("什么是人工智能", "general"),
    ]
    
    results = []
    for query, expected_intent in test_cases:
        intent = planner._classify_intent(query)
        passed = intent == expected_intent
        status = "✅" if passed else "❌"
        
        print(f"{status} '{query}' -> {intent} (期望: {expected_intent})")
        results.append(passed)
    
    passed_count = sum(results)
    total_count = len(results)
    print(f"\n通过率: {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)")
    
    return all(results)


def test_rag_in_summarizer():
    """测试2: 验证 Summarizer 是否集成 RAG"""
    print("\n" + "="*60)
    print("【测试2】Summarizer RAG 集成检查")
    print("="*60)
    
    from agents.summarizer_agent import SummarizerAgent
    import inspect
    
    summarizer = SummarizerAgent()
    
    # 检查1: 是否有 retriever 属性
    has_retriever = hasattr(summarizer, 'retriever')
    print(f"{'✅' if has_retriever else '❌'} Summarizer 有 retriever 属性")
    
    # 检查2: 是否有 _get_knowledge_context 方法
    has_method = hasattr(summarizer, '_get_knowledge_context')
    print(f"{'✅' if has_method else '❌'} Summarizer 有 _get_knowledge_context 方法")
    
    # 检查3: run 方法中是否调用知识库检索
    run_source = inspect.getsource(summarizer.run)
    calls_rag = '_get_knowledge_context' in run_source
    print(f"{'✅' if calls_rag else '❌'} Summarizer.run 调用了知识库检索")
    
    # 检查4: SUMMARIZER_PROMPT 中是否有 knowledge_context 参数
    from prompts.summarizer import SUMMARIZER_PROMPT
    has_param = 'knowledge_context' in SUMMARIZER_PROMPT
    print(f"{'✅' if has_param else '❌'} SUMMARIZER_PROMPT 包含 knowledge_context 参数")
    
    all_checks = [has_retriever, has_method, calls_rag, has_param]
    print(f"\n集成状态: {sum(all_checks)}/4 检查通过")
    
    return all(all_checks)


def test_workflow_routing():
    """测试3: 工作流三分支路由"""
    print("\n" + "="*60)
    print("【测试3】工作流三分支路由")
    print("="*60)
    
    from graph.workflow import create_multi_branch_graph
    
    graph = create_multi_branch_graph()
    
    # 测试用例
    test_cases = [
        {
            "name": "股票分析分支",
            "state": {
                'user_query': '分析茅台的投资价值',
                'intent': 'stock',
                'stock_code': 'sh.600519',
                'company_name': '贵州茅台',
                'market': '上海',
            },
            "should_have": ['fundamental_analysis', 'technical_analysis', 'valuation_analysis', 'news_analysis', 'final_report']
        },
        {
            "name": "公司知识分支",
            "state": {
                'user_query': '公司请假流程',
                'intent': 'company',
            },
            "should_have": ['final_report']
        },
        {
            "name": "通用问答分支",
            "state": {
                'user_query': '什么是人工智能',
                'intent': 'general',
            },
            "should_have": ['final_report']
        }
    ]
    
    results = []
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        print(f"  查询: {test_case['state']['user_query']}")
        print(f"  意图: {test_case['state']['intent']}")
        
        try:
            # 执行工作流 (仅检查路由，不实际执行LLM)
            # 由于实际执行需要API，我们这里只检查图结构
            from langgraph.graph import END
            
            # 模拟路由
            intent = test_case['state']['intent']
            if intent == 'stock':
                expected_nodes = ['planner', 'fundamental', 'technical', 'valuation', 'news', 'summarizer']
            elif intent == 'company':
                expected_nodes = ['planner', 'company_qa']
            else:  # general
                expected_nodes = ['planner', 'general_qa']
            
            # 获取图节点
            graph_nodes = list(graph.get_graph().nodes.keys())
            
            # 检查必要节点是否存在
            all_present = all(node in graph_nodes for node in expected_nodes)
            status = "✅" if all_present else "❌"
            print(f"  {status} 必要节点存在: {expected_nodes}")
            
            results.append(all_present)
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")
            results.append(False)
    
    passed_count = sum(results)
    total_count = len(results)
    print(f"\n通过率: {passed_count}/{total_count}")
    
    return all(results)


def test_end_to_end_stock_with_rag():
    """测试4: 端到端测试 - 股票分析 + RAG"""
    print("\n" + "="*60)
    print("【测试4】端到端测试 - 股票分析 + RAG")
    print("="*60)
    
    from rag.retriever.stock_retriever import StockRetriever
    
    # 检查知识库状态
    retriever = StockRetriever()
    doc_count = retriever.count()
    print(f"向量库文档数: {doc_count}")
    
    if doc_count == 0:
        print("\n⚠️  向量库为空，尝试索引知识库...")
        
        # 检查是否有PDF文件
        knowledge_dir = config.STOCK_KNOWLEDGE_DIR
        if os.path.exists(knowledge_dir):
            pdf_files = [f for f in os.listdir(knowledge_dir) if f.endswith('.pdf')]
            print(f"找到 {len(pdf_files)} 个PDF文件")
            
            if pdf_files:
                print("正在索引...")
                count = retriever.index_knowledge_dir()
                print(f"✅ 索引完成，添加了 {count} 个文档块")
            else:
                print("❌ 知识库目录中没有PDF文件")
                print(f"   请将年报/研报放入: {knowledge_dir}")
                return False
        else:
            print(f"❌ 知识库目录不存在: {knowledge_dir}")
            return False
    
    # 测试检索功能
    test_query = "公司的主营业务"
    print(f"\n测试检索: '{test_query}'")
    result = retriever.search(test_query, k=2)
    
    if result:
        print(f"✅ 检索成功 (前150字):\n{result[:150]}...")
        return True
    else:
        print("❌ 检索失败，未找到相关内容")
        return False


def test_company_qa_branch():
    """测试5: 公司知识问答分支"""
    print("\n" + "="*60)
    print("【测试5】公司知识问答分支")
    print("="*60)
    
    from rag.retriever.company_retriever import CompanyRetriever
    
    retriever = CompanyRetriever()
    
    # 添加测试知识
    test_knowledge = """
    公司请假流程：
    1. 登录OA系统
    2. 填写请假申请单
    3. 选择请假类型（年假/事假/病假）
    4. 提交给直属领导审批
    5. 领导审批通过后生效
    
    报销流程：
    1. 准备报销单据
    2. 在财务系统提交报销申请
    3. 附上发票和凭证
    4. 等待财务审核
    5. 审核通过后到账
    """
    
    print("添加测试知识...")
    count = retriever.add_text(test_knowledge, "员工手册")
    print(f"✅ 添加了 {count} 个文档块")
    
    # 测试检索
    test_cases = [
        "如何请假",
        "报销流程是什么",
        "怎么提交报销",
    ]
    
    results = []
    for query in test_cases:
        print(f"\n查询: '{query}'")
        result = retriever.search(query, k=1)
        
        if result and len(result) > 0:
            print(f"✅ 检索成功 (前100字):\n  {result[:100]}...")
            results.append(True)
        else:
            print("❌ 检索失败")
            results.append(False)
    
    # 清理测试数据
    retriever.clear()
    print("\n✅ 测试数据已清理")
    
    passed_count = sum(results)
    total_count = len(results)
    print(f"\n通过率: {passed_count}/{total_count}")
    
    return all(results)


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("          三分支路由 + RAG 集成测试")
    print("="*70)
    
    results = {}
    
    # 测试1: 意图识别
    try:
        results['意图识别'] = test_intent_classification()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['意图识别'] = False
    
    # 测试2: RAG集成检查
    try:
        results['RAG集成检查'] = test_rag_in_summarizer()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['RAG集成检查'] = False
    
    # 测试3: 工作流路由
    try:
        results['工作流路由'] = test_workflow_routing()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['工作流路由'] = False
    
    # 测试4: 股票RAG端到端
    try:
        results['股票RAG端到端'] = test_end_to_end_stock_with_rag()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['股票RAG端到端'] = False
    
    # 测试5: 公司知识问答
    try:
        results['公司知识问答'] = test_company_qa_branch()
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        results['公司知识问答'] = False
    
    # 汇总结果
    print("\n" + "="*70)
    print("          测试结果汇总")
    print("="*70)
    
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    print(f"\n总计: {passed_count}/{total_count} 通过")
    print(f"通过率: {passed_count/total_count*100:.1f}%\n")
    
    # 总结
    print("="*70)
    print("          测试总结")
    print("="*70)
    
    if results.get('意图识别', False):
        print("✅ PlannerAgent 能够准确识别三种意图 (stock/company/general)")
    else:
        print("❌ PlannerAgent 意图识别存在问题")
    
    if results.get('RAG集成检查', False):
        print("✅ SummarizerAgent 已集成 RAG，会从知识库检索相关内容")
    else:
        print("❌ SummarizerAgent RAG集成不完整")
    
    if results.get('工作流路由', False):
        print("✅ 工作流图包含所有三个分支的必要节点")
    else:
        print("❌ 工作流图结构存在问题")
    
    if results.get('股票RAG端到端', False):
        print("✅ 股票知识库可用，RAG检索功能正常")
    else:
        print("⚠️  股票知识库需要添加PDF文件")
    
    if results.get('公司知识问答', False):
        print("✅ 公司知识问答分支工作正常")
    else:
        print("❌ 公司知识问答分支存在问题")
    
    print("="*70 + "\n")
    
    return all(results.values())


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
