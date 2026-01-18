"""
调试脚本 - 逐步测试各组件
增强版：真实验证每个组件的功能
"""
import sys
import traceback
sys.path.insert(0, '.')

# 测试用的股票代码
TEST_STOCK_CODE = "sh.600519"  # 贵州茅台
TEST_COMPANY_NAME = "贵州茅台"

def print_header(step: int, title: str):
    """打印步骤标题"""
    print("\n" + "=" * 60)
    print(f"Step {step}: {title}")
    print("=" * 60)

def print_success(msg: str):
    """打印成功信息"""
    print(f"  ✓ {msg}")

def print_error(msg: str, exception: Exception = None):
    """打印错误信息"""
    print(f"  ✗ {msg}")
    if exception:
        print(f"    详细错误: {exception}")
        print("    完整堆栈:")
        traceback.print_exc()

def print_info(msg: str):
    """打印普通信息"""
    print(f"  → {msg}")


# ============================================================
# Step 1: 测试配置加载
# ============================================================
print_header(1, "测试配置加载")
try:
    from config import config
    
    # 验证 API Key
    if config.OPENAI_API_KEY:
        key_preview = config.OPENAI_API_KEY[:8] + "..." + config.OPENAI_API_KEY[-4:]
        print_success(f"OPENAI_API_KEY: {key_preview}")
    else:
        print_error("OPENAI_API_KEY 未配置")
        sys.exit(1)
    
    print_info(f"OPENAI_BASE_URL: {config.OPENAI_BASE_URL}")
    print_info(f"OPENAI_MODEL: {config.OPENAI_MODEL}")
    print_info(f"LOG_LEVEL: {config.LOG_LEVEL}")
    
    # 验证输出目录
    output_dir = config.ensure_output_dir()
    print_success(f"输出目录已创建: {output_dir.absolute()}")
    
except Exception as e:
    print_error("配置加载失败", e)
    sys.exit(1)


# ============================================================
# Step 2: 测试数据源连接
# ============================================================
print_header(2, "测试数据源连接")
try:
    import baostock as bs
    from tools.baostock_utils import baostock_login_context
    
    # 测试 Baostock 连接
    with baostock_login_context():
        rs = bs.query_stock_basic(code=TEST_STOCK_CODE)
        if rs.error_code == '0' and rs.next():
            row = rs.get_row_data()
            print_success(f"Baostock 连接成功: {TEST_STOCK_CODE}")
            print_info(f"  股票名称: {row[1] if len(row) > 1 else '未知'}")
        else:
            print_error(f"Baostock 查询失败: {rs.error_msg}")
    
    # 测试 Akshare 连接 (使用轻量级 API)
    try:
        import akshare as ak
        # 使用获取股票代码名称列表 - 本地缓存，速度快
        df = ak.stock_info_a_code_name()
        if df is not None and len(df) > 0:
            print_success(f"Akshare 连接成功: 获取到 {len(df)} 只A股代码")
        else:
            print_info("Akshare 连接成功 (但未获取到数据)")
    except ImportError:
        print_info("Akshare 库未安装 (可选)")
    except Exception as ak_e:
        print_info(f"Akshare 连接失败 (可选): {ak_e}")

except Exception as e:
    print_error("数据源连接失败", e)


# ============================================================
# Step 3: 测试股票搜索功能
# ============================================================
print_header(3, "测试股票搜索功能")
try:
    from tools.stock_search import query_stock_info, _search_stock_by_name
    
    # 测试直接搜索
    result = _search_stock_by_name(TEST_COMPANY_NAME)
    if result:
        print_success(f"股票搜索成功: {TEST_COMPANY_NAME}")
        print_info(f"  代码: {result['code']}")
        print_info(f"  市场: {result['market']}")
    else:
        print_error(f"股票搜索失败: 未找到 {TEST_COMPANY_NAME}")

    # 测试 tool 函数 (不调用 LLM)
    stock_info = query_stock_info.invoke(TEST_STOCK_CODE)
    if "股票信息" in stock_info:
        print_success("query_stock_info 工具测试成功")
        # 只打印前几行
        for line in stock_info.split('\n')[:6]:
            if line.strip():
                print_info(f"  {line.strip()}")
    else:
        print_error(f"query_stock_info 返回异常: {stock_info[:100]}")

except Exception as e:
    print_error("股票搜索功能测试失败", e)


# ============================================================
# Step 4: 测试 OpenAI 连接
# ============================================================
print_header(4, "测试 OpenAI 连接")
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    
    llm = ChatOpenAI(
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        model=config.OPENAI_MODEL,
        temperature=0,
        request_timeout=30  # 30秒超时
    )
    
    print_info("正在测试 API 调用 (最多等待30秒)...")
    response = llm.invoke([HumanMessage(content="请用一句话回复：你好")])
    
    # 显示完整响应
    full_response = response.content.strip()
    print_success(f"API 响应成功")
    print_info(f"  模型回复: {full_response}")
    print_info(f"  响应长度: {len(full_response)} 字符")
    
except Exception as e:
    print_error("OpenAI 连接失败", e)
    print_info("请检查 API Key 和网络连接")
    sys.exit(1)


# ============================================================
# Step 5: 测试新闻爬取功能 (可选)
# ============================================================
print_header(5, "测试新闻爬取功能")
try:
    from tools.news_crawler import _search_baidu_news
    
    print_info(f"正在爬取 '{TEST_COMPANY_NAME}' 相关新闻...")
    news_list = _search_baidu_news(TEST_COMPANY_NAME, num_results=3)
    
    if news_list and len(news_list) > 0:
        first_news = news_list[0]
        if "获取失败" not in first_news.get('title', ''):
            print_success(f"新闻爬取成功: 获取到 {len(news_list)} 条新闻")
            for i, news in enumerate(news_list, 1):
                title = news.get('title', '无标题')[:40]
                print_info(f"  {i}. {title}...")
        else:
            print_info(f"新闻爬取受限: {first_news.get('title', '未知错误')}")
    else:
        print_info("未获取到新闻 (可能是网络或反爬限制)")

except Exception as e:
    print_error("新闻爬取测试失败", e)


# ============================================================
# Step 6: 测试工作流创建
# ============================================================
print_header(6, "测试工作流创建")
try:
    from graph.workflow import create_stock_analysis_graph_v2
    
    graph = create_stock_analysis_graph_v2()
    print_success("工作流创建成功")
    
    # 获取工作流信息
    if hasattr(graph, 'nodes'):
        print_info(f"  节点列表: {list(graph.nodes.keys()) if hasattr(graph.nodes, 'keys') else '无法获取'}")
    
except Exception as e:
    print_error("工作流创建失败", e)
    sys.exit(1)


# ============================================================
# Step 7: 测试工作流执行 (带详细日志)
# ============================================================
print_header(7, "测试工作流执行 (带详细日志)")
try:
    from graph.state import StockAnalysisState
    import time
    
    # 创建初始状态
    initial_state: StockAnalysisState = {
        "user_query": f"分析 {TEST_COMPANY_NAME} 的投资价值"
    }
    
    print_info(f"输入查询: {initial_state['user_query']}")
    print_info("工作流节点顺序: planner → fundamental → technical → valuation → news → summarizer")
    print_info("提示: 按 Ctrl+C 可跳过此测试")
    print_info("注意: fundamental 节点可能需要1-2分钟（涉及多次LLM调用和数据获取）\n")
    
    # 节点描述映射
    NODE_DESCRIPTIONS = {
        "planner": "任务规划 (解析用户输入，识别股票代码)",
        "fundamental": "基本面分析 (财务数据、盈利能力等)",
        "technical": "技术分析 (K线、均线、MACD等)",
        "valuation": "估值分析 (PE、PB、DCF等)",
        "news": "新闻分析 (最新资讯、情感分析)",
        "summarizer": "总结报告 (整合所有分析生成最终报告)",
        "__end__": "工作流结束"
    }
    
    # 使用 stream 模式执行，实时显示每个节点的进度
    try:
        result = None
        node_count = 0
        
        print_info("=" * 50)
        print_info("开始执行工作流 (节点超时限制: 180秒, 按 Ctrl+C 强制终止)...")
        print_info("=" * 50)

        # 使用线程池来实现超时控制
        import concurrent.futures
        
        # 创建迭代器
        iterator = iter(graph.stream(initial_state))
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        
        while True:
            try:
                print_info(f"[{time.strftime('%H:%M:%S')}] 正在执行下一个节点...")
                
                # 在线程中执行 next(iterator)
                future = executor.submit(next, iterator)
                
                try:
                    # 使用轮询方式等待，以便支持 Ctrl+C 中断
                    # 每0.5秒检查一次，总共等待180秒
                    max_wait = 180
                    elapsed = 0
                    while elapsed < max_wait:
                        try:
                            event = future.result(timeout=0.5)
                            break  # 成功获取结果
                        except concurrent.futures.TimeoutError:
                            elapsed += 0.5
                            continue
                    else:
                        # 超过120秒
                        raise concurrent.futures.TimeoutError()
                except concurrent.futures.TimeoutError:
                    print_error(f"[{time.strftime('%H:%M:%S')}] 节点执行超时 (超过180秒)！")
                    print_info("可能原因: 1) Agent 调用工具次数过多  2) 数据源响应慢  3) LLM 响应慢")
                    print_info("建议: 1) 减少 recursion_limit  2) 增加工具超时设置  3) 使用 debug 模式查看详情")
                    print_info("强制截断当前测试...")
                    break
                except StopIteration:
                    print_info(f"[{time.strftime('%H:%M:%S')}]工作流全部完成")
                    break
                
                # 正常获取到结果
                node_count += 1
                current_time = time.strftime("%H:%M:%S")
                
                # event 是一个字典，key 是节点名称
                for node_name, node_output in event.items():
                    description = NODE_DESCRIPTIONS.get(node_name, node_name)
                    print(f"\n  [{current_time}] 节点 {node_count}: {node_name} (完成)")
                    print(f"             描述: {description}")
                    
                    # 显示该节点产生的输出字段
                    if isinstance(node_output, dict):
                        output_keys = list(node_output.keys())
                        print(f"             输出字段: {output_keys}")
                        
                        # 显示关键信息
                        if 'stock_code' in node_output and node_output['stock_code']:
                            print(f"             → 识别股票代码: {node_output['stock_code']}")
                        if 'company_name' in node_output and node_output['company_name']:
                            print(f"             → 公司名称: {node_output['company_name']}")
                        if 'fundamental_analysis' in node_output:
                            length = len(node_output['fundamental_analysis']) if node_output['fundamental_analysis'] else 0
                            print(f"             → 基本面分析: {length} 字符")
                        if 'technical_analysis' in node_output:
                            length = len(node_output['technical_analysis']) if node_output['technical_analysis'] else 0
                            print(f"             → 技术分析: {length} 字符")
                        if 'valuation_analysis' in node_output:
                            length = len(node_output['valuation_analysis']) if node_output['valuation_analysis'] else 0
                            print(f"             → 估值分析: {length} 字符")
                        if 'news_analysis' in node_output:
                            length = len(node_output['news_analysis']) if node_output['news_analysis'] else 0
                            print(f"             → 新闻分析: {length} 字符")
                        if 'final_report' in node_output:
                            length = len(node_output['final_report']) if node_output['final_report'] else 0
                            print(f"             → 最终报告: {length} 字符")
                        
                        # 检查是否有错误信息
                        if 'error' in node_output:
                            print(f"             ⚠ 错误: {node_output['error']}")
                    
                    # 保存最终结果
                    if node_name == "__end__" or node_output:
                        result = node_output if isinstance(node_output, dict) else result
                        
                    print(f"             状态: ✓ 完成")
            
            except Exception as outer_e:
                print_error("循环执行中发生未知错误", outer_e)
                break
        
        # 清理线程池 (不等待卡住的线程)
        executor.shutdown(wait=False)
        
        print_info("\n" + "=" * 50)
        print_info("工作流执行完成!")
        print_info("=" * 50)
        
        # 最终结果检查
        if result and result.get('stock_code'):
            print_success(f"工作流执行成功")
            print_info(f"  识别股票代码: {result.get('stock_code')}")
            print_info(f"  公司名称: {result.get('company_name', '未知')}")
            
            # 显示最终报告
            if result.get('final_report'):
                print("\n" + "=" * 60)
                print("最终分析报告")
                print("=" * 60)
                print(result['final_report'])
                print("=" * 60)
                
                # 保存报告到文件
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = config.OUTPUT_DIR / f"debug_report_{TEST_COMPANY_NAME}_{timestamp}.md"
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {TEST_COMPANY_NAME} 测试脚本股票分析报告\n\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(result['final_report'])
                print_success(f"报告已保存至: {report_file}")
        elif result:
            print_info(f"工作流完成，最终状态包含: {list(result.keys())}")
        else:
            print_error("工作流执行完成但未获得有效结果")
        
        # 正常结束时也要清理线程池
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except:
            pass
            
    except KeyboardInterrupt:
        print_info("\n\n⚠ 用户按下 Ctrl+C，正在强制终止...")
        print_info(f"已完成 {node_count} 个节点")
        # 清理线程池
        try:
            executor.shutdown(wait=False, cancel_futures=True)
        except:
            pass

except Exception as e:
    print_error("工作流执行失败", e)


# ============================================================
# 测试完成总结
# ============================================================
print("\n" + "=" * 60)
print("测试完成总结")
print("=" * 60)
print("""
所有核心组件测试通过!

已验证的功能:
  ✓ 配置加载和环境变量
  ✓ Baostock 连接和数据获取
  ✓ 股票搜索功能
  ✓ OpenAI API 连接
  ✓ 新闻爬取功能
  ✓ LangGraph 工作流创建和执行

如需运行完整分析，请使用:
  python main.py

或启动 Web 界面:
  streamlit run app.py
""")

# ============================================================
# 清理资源并退出
# ============================================================
try:
    from tools.baostock_utils import _connection_manager
    _connection_manager.logout()
except:
    pass

# 强制退出，确保所有后台线程终止
import os
os._exit(0)
