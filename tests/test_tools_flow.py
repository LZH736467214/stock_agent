"""
测试实际工具调用过程
检查是哪一步卡住
"""
import sys
import time
sys.path.insert(0, '.')

print("=" * 60)
print("工具调用流程测试")
print("=" * 60)

from config import config
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from tools.financial_reports import get_profit_data, get_growth_data, get_balance_data

# 只使用3个工具进行测试
tools = [get_profit_data, get_growth_data, get_balance_data]

print(f"\nModel: {config.OPENAI_MODEL}")
print(f"测试工具: {[t.name for t in tools]}")

# 确保 Baostock 连接
print("\n[1] 确保 Baostock 连接...")
from tools.baostock_utils import ensure_baostock_connection
ensure_baostock_connection()
print("    连接成功")

# 创建 LLM
print("\n[2] 创建 LLM 和 ReAct Agent...")
llm = ChatOpenAI(
    api_key=config.OPENAI_API_KEY,
    base_url=config.OPENAI_BASE_URL,
    model=config.OPENAI_MODEL,
    temperature=0,
    request_timeout=120
)

agent = create_react_agent(model=llm, tools=tools)
print("    创建成功")

# 测试 prompt
prompt = """分析贵州茅台(sh.600519)的基本面。

重要规则：
1. 只调用一次 get_profit_data 工具
2. 参数: code="sh.600519", year=2024, quarter=3
3. 获取数据后直接输出分析结果

请开始分析。"""

messages = [
    SystemMessage(content="你是一个股票分析师。每次只调用一个工具。"),
    HumanMessage(content=prompt)
]

# 使用 stream 模式执行
print("\n[3] 开始执行 Agent (stream 模式)...")
print("-" * 50)

start_time = time.time()
step = 0

try:
    for event in agent.stream({"messages": messages}, config={"recursion_limit": 10}):
        step += 1
        elapsed = time.time() - start_time
        current_time = time.strftime("%H:%M:%S")
        
        for key, value in event.items():
            print(f"\n[{current_time}] (+{elapsed:.1f}s) Step {step}: {key}")
            
            if key == "agent":
                if "messages" in value:
                    for msg in value["messages"]:
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tc in msg.tool_calls:
                                print(f"    → 调用工具: {tc['name']}")
                                print(f"    → 参数: {tc['args']}")
                        elif hasattr(msg, 'content') and msg.content:
                            print(f"    → 响应长度: {len(msg.content)} 字符")
                            print(f"    → 预览: {msg.content[:200]}...")
            
            elif key == "tools":
                if "messages" in value:
                    for msg in value["messages"]:
                        if hasattr(msg, 'content'):
                            print(f"    → 工具返回: {len(msg.content)} 字符")
                            if len(msg.content) < 100:
                                print(f"    → 内容: {msg.content}")

    total_time = time.time() - start_time
    print(f"\n" + "-" * 50)
    print(f"执行完成! 总耗时: {total_time:.2f}秒, 共 {step} 步")

except KeyboardInterrupt:
    print("\n\n用户中断")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n执行出错! 耗时: {elapsed:.2f}秒")
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
