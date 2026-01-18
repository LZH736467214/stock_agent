"""
测试 LLM API 响应速度
测试不同数据量下的响应时间
"""
import sys
import time
sys.path.insert(0, '.')

from config import config
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

print("=" * 60)
print("LLM API 响应速度测试")
print("=" * 60)
print(f"Model: {config.OPENAI_MODEL}")
print(f"Base URL: {config.OPENAI_BASE_URL}")

llm = ChatOpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    model=config.OPENAI_MODEL,
    temperature=0,
    request_timeout=120  # 2分钟超时
)

# 测试1: 简单请求
print("\n" + "-" * 50)
print("测试1: 简单请求 (小数据量)")
print("-" * 50)
start = time.time()
response = llm.invoke([HumanMessage(content="回复OK")])
elapsed = time.time() - start
print(f"响应: {response.content}")
print(f"耗时: {elapsed:.2f}秒")

# 测试2: 模拟1个工具返回
print("\n" + "-" * 50)
print("测试2: 模拟1个工具返回 (~500字符)")
print("-" * 50)
tool_result = """### sh.600519 2024Q3 盈利能力数据

| code | pubDate | statDate | roeAvg | npMargin | gpMargin | netProfit | epsTTM |
|:--|:--|:--|:--|:--|:--|:--|:--|
| sh.600519 | 2024-10-31 | 2024-09-30 | 8.2345 | 52.1234 | 91.2345 | 50912345678 | 40.12 |

说明：ROE较高，盈利能力优秀。"""

messages = [
    HumanMessage(content="分析这个数据"),
    AIMessage(content="", tool_calls=[{"id": "call_1", "name": "get_profit_data", "args": {}}]),
    ToolMessage(content=tool_result, tool_call_id="call_1"),
    HumanMessage(content="请分析盈利能力")
]
start = time.time()
response = llm.invoke(messages)
elapsed = time.time() - start
print(f"响应长度: {len(response.content)} 字符")
print(f"耗时: {elapsed:.2f}秒")

# 测试3: 模拟6个工具返回 (约3000字符)
print("\n" + "-" * 50)
print("测试3: 模拟6个工具返回 (~3000字符)")
print("-" * 50)

messages = [HumanMessage(content="分析贵州茅台的基本面")]
for i in range(6):
    messages.append(AIMessage(content="", tool_calls=[{"id": f"call_{i}", "name": f"tool_{i}", "args": {}}]))
    messages.append(ToolMessage(content=tool_result, tool_call_id=f"call_{i}"))
messages.append(HumanMessage(content="请综合分析"))

start = time.time()
response = llm.invoke(messages)
elapsed = time.time() - start
print(f"输入消息数: {len(messages)}")
print(f"响应长度: {len(response.content)} 字符")
print(f"耗时: {elapsed:.2f}秒")

# 测试4: 模拟24个工具返回 (约12000字符) - 这是实际场景
print("\n" + "-" * 50)
print("测试4: 模拟24个工具返回 (~12000字符) ← 实际场景")
print("-" * 50)

messages = [HumanMessage(content="分析贵州茅台的基本面，请调用所有财务工具")]
for i in range(24):
    messages.append(AIMessage(content="", tool_calls=[{"id": f"call_{i}", "name": f"tool_{i}", "args": {}}]))
    messages.append(ToolMessage(content=tool_result, tool_call_id=f"call_{i}"))
messages.append(HumanMessage(content="请综合分析所有数据并给出报告"))

total_chars = sum(len(m.content) if hasattr(m, 'content') else 0 for m in messages)
print(f"输入消息数: {len(messages)}")
print(f"总字符数: ~{total_chars} 字符")
print("正在调用 API (可能需要较长时间)...")

start = time.time()
try:
    response = llm.invoke(messages)
    elapsed = time.time() - start
    print(f"响应长度: {len(response.content)} 字符")
    print(f"耗时: {elapsed:.2f}秒")
    print(f"\n响应预览:\n{response.content[:500]}...")
except Exception as e:
    elapsed = time.time() - start
    print(f"调用失败! 耗时: {elapsed:.2f}秒")
    print(f"错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
