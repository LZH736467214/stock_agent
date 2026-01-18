"""
专门测试 fundamental_agent 的调试脚本
用于诊断为什么 fundamental 节点会超时
"""
import sys
sys.path.insert(0, '.')

TEST_STOCK_CODE = "sh.600519"
TEST_COMPANY_NAME = "贵州茅台"

print("=" * 70)
print("Fundamental Agent 深度调试")
print("=" * 70)

# ============================================================
# 测试1: 直接测试财务数据工具
# ============================================================
print("\n[测试1] 直接测试财务数据工具")
print("-" * 70)

try:
    from tools.financial_reports import (
        get_profit_data,
        get_operation_data,
        get_growth_data,
    )
    import time
    
    # 测试单个工具调用的耗时
    tools_to_test = [
        ("盈利能力", get_profit_data),
        ("营运能力", get_operation_data),
        ("成长能力", get_growth_data),
    ]
    
    for tool_name, tool_func in tools_to_test:
        print(f"\n  测试工具: {tool_name}")
        start = time.time()
        
        try:
            result = tool_func.invoke({
                "code": TEST_STOCK_CODE,
                "year": 2024,
                "quarter": 3
            })
            elapsed = time.time() - start
            
            if "失败" in result or "错误" in result:
                print(f"    ✗ 失败 ({elapsed:.2f}秒): {result[:100]}")
            else:
                result_lines = result.split('\n')[:5]  # 只显示前5行
                print(f"    ✓ 成功 ({elapsed:.2f}秒)")
                print(f"    返回数据预览: {len(result)} 字符")
                for line in result_lines:
                    if line.strip():
                        print(f"      {line}")
        except Exception as e:
            elapsed = time.time() - start
            print(f"    ✗ 异常 ({elapsed:.2f}秒): {e}")

except Exception as e:
    print(f"  ✗ 工具测试失败: {e}")
    import traceback
    traceback.print_exc()


# ============================================================
# 测试2: 测试 FundamentalAgent 的初始化
# ============================================================
print("\n\n[测试2] 测试 FundamentalAgent 初始化")
print("-" * 70)

try:
    from agents.fundamental_agent import FundamentalAgent
    
    agent = FundamentalAgent()
    print(f"  ✓ Agent 创建成功")
    print(f"    工具数量: {len(agent.tools)}")
    print(f"    工具列表: {[t.name for t in agent.tools]}")
    print(f"    递归限制: {agent.recursion_limit}")
    print(f"    模型: {agent.model}")
    
except Exception as e:
    print(f"  ✗ Agent 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


# ============================================================
# 测试3: 测试 Agent 执行 (启用调试模式)
# ============================================================
print("\n\n[测试3] 测试 Agent 执行 (启用调试模式)")
print("-" * 70)
print("  注意: 这将显示 Agent 的每一步操作，可能需要 1-2 分钟")
print("  按 Ctrl+C 可随时中断\n")

try:
    from langchain_core.messages import HumanMessage
    from prompts.fundamental import FUNDAMENTAL_PROMPT
    import time
    
    # 构建输入
    prompt = FUNDAMENTAL_PROMPT.format(
        company_name=TEST_COMPANY_NAME,
        stock_code=TEST_STOCK_CODE
    )
    
    print(f"  提示词长度: {len(prompt)} 字符")
    print(f"  提示词预览:")
    for line in prompt.split('\n')[:10]:
        if line.strip():
            print(f"    {line[:100]}")
    
    messages = [HumanMessage(content=prompt)]
    
    print(f"\n  开始执行 (调试模式)...")
    print(f"  [{time.strftime('%H:%M:%S')}] 启动")
    
    start_time = time.time()
    
    # 使用调试模式执行
    result = agent.invoke({'messages': messages}, debug=True)
    
    elapsed = time.time() - start_time
    
    print(f"\n  [{time.strftime('%H:%M:%S')}] 执行完成")
    print(f"  总耗时: {elapsed:.2f} 秒")
    
    # 提取分析结果
    if result and 'messages' in result:
        ai_message = result['messages'][-1]
        analysis = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)
        
        print(f"\n  最终分析长度: {len(analysis)} 字符")
        print(f"  分析预览 (前500字符):")
        print("-" * 70)
        print(analysis[:500])
        print("-" * 70)
    else:
        print(f"  ✗ 未获得有效结果: {result}")

except KeyboardInterrupt:
    print(f"\n\n  用户中断执行")
    elapsed = time.time() - start_time
    print(f"  执行时长: {elapsed:.2f} 秒")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n  ✗ 执行失败 ({elapsed:.2f}秒): {e}")
    import traceback
    traceback.print_exc()


# ============================================================
# 测试4: 测试简化版 Agent (减少工具数量)
# ============================================================
print("\n\n[测试4] 测试简化版 Agent (只使用1个工具)")
print("-" * 70)

try:
    from agents.base_agent import BaseAgent
    from langchain_core.messages import HumanMessage
    import time
    
    # 创建只有一个工具的简化版 Agent
    class SimpleFundamentalAgent(BaseAgent):
        def __init__(self):
            from tools.financial_reports import get_profit_data
            super().__init__(
                name="简化基本面Agent",
                tools=[get_profit_data],  # 只用一个工具
                system_prompt=f"""你是一个股票分析助手。
请使用工具获取 {TEST_STOCK_CODE} 的 2024Q3 盈利能力数据，然后简要分析。
只调用一次工具即可，不要重复调用。"""
            )
        
        def run(self, state: dict) -> dict:
            pass
    
    simple_agent = SimpleFundamentalAgent()
    print(f"  ✓ 简化 Agent 创建成功 (工具数: {len(simple_agent.tools)})")
    
    messages = [HumanMessage(content="请获取数据并分析")]
    
    print(f"  开始执行 (30秒超时保护)...")
    start = time.time()
    
    # 使用线程 + 超时来防止永久卡住
    import concurrent.futures
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    
    future = executor.submit(simple_agent.invoke, {'messages': messages}, False)
    
    try:
        result = future.result(timeout=30)
        elapsed = time.time() - start
        print(f"  ✓ 执行完成 ({elapsed:.2f}秒)")
        
        if result and 'messages' in result:
            ai_message = result['messages'][-1]
            print(f"  响应长度: {len(ai_message.content)} 字符")
            print(f"  响应预览: {ai_message.content[:200]}")
    except concurrent.futures.TimeoutError:
        elapsed = time.time() - start
        print(f"  ✗ 执行超时 ({elapsed:.2f}秒)")
        print(f"  问题: agent.invoke() 永久卡住，可能原因:")
        print(f"    1. LLM API 调用没有响应（API 提供商问题）")
        print(f"    2. ReAct Agent 进入死循环")
        print(f"    3. 某个工具调用永久阻塞")
        executor.shutdown(wait=False)
    finally:
        executor.shutdown(wait=False)

except Exception as e:
    print(f"  ✗ 简化测试失败: {e}")
    import traceback
    traceback.print_exc()


print("\n" + "=" * 70)
print("调试完成")
print("=" * 70)
print("""
根据以上测试结果:
  - 如果测试1失败 → 数据源有问题
  - 如果测试2失败 → Agent 配置有问题
  - 如果测试3超时 → Agent 调用工具次数过多或 LLM 响应慢
  - 如果测试4成功但测试3失败 → 工具太多导致 Agent 决策复杂
""")
