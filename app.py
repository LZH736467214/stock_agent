"""
多Agent股票顾问系统 - Web界面 (Streamlit)
Apple Design Language风格
"""
import streamlit as st
import asyncio
import textwrap
from datetime import datetime
from graph.workflow import create_stock_analysis_graph_v2
from config import config

# 设置页面配置
st.set_page_config(
    page_title="Agentic Stock Advisor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apple Design Language CSS
st.markdown("""
<style>
/* 导入SF Pro风格字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 全局样式 */
.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(180deg, #f5f5f7 0%, #ffffff 100%);
}

/* 隐藏Streamlit默认元素 */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 2rem; padding-bottom: 2rem;}

/* 标题样式 - Apple风格渐变 */
.apple-title {
    background: linear-gradient(135deg, #007AFF 0%, #5856D6 50%, #AF52DE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.8rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
    text-align: center;
}

.apple-subtitle {
    color: #86868b;
    font-size: 1.1rem;
    font-weight: 400;
    text-align: center;
    margin-bottom: 2rem;
}

/* 磨砂玻璃卡片 */
.glass-card {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 18px;
    border: 1px solid rgba(255, 255, 255, 0.18);
    padding: 28px;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.04),
        0 1px 3px rgba(0, 0, 0, 0.03);
    margin-bottom: 24px;
}

/* 输入框样式 */
.stTextInput > div > div > input {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 1.5px solid #d2d2d7 !important;
    border-radius: 12px !important;
    padding: 14px 18px !important;
    font-size: 16px !important;
    transition: all 0.2s ease !important;
}

.stTextInput > div > div > input:focus {
    border-color: #007AFF !important;
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.15) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #86868b !important;
}

/* 按钮样式 - Apple风格 */
.stButton > button {
    background: linear-gradient(135deg, #007AFF 0%, #0051D4 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 28px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(0, 122, 255, 0.35) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0, 122, 255, 0.45) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* 进度条样式 */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #007AFF 0%, #5856D6 100%) !important;
    border-radius: 8px !important;
}

.stProgress > div > div {
    background: #e8e8ed !important;
    border-radius: 8px !important;
}

/* 状态文本样式 */
.status-text {
    color: #1d1d1f;
    font-size: 15px;
    font-weight: 500;
    padding: 8px 0;
}

.status-icon {
    display: inline-block;
    margin-right: 8px;
}

/* 工具调用日志样式 */
.tool-log {
    background: #1d1d1f;
    border-radius: 12px;
    padding: 16px;
    font-family: 'SF Mono', 'Menlo', 'Monaco', monospace;
    font-size: 13px;
    color: #00d4aa;
    max-height: 400px;
    overflow-y: auto;
    margin: 16px 0;
}

.tool-log-entry {
    padding: 6px 0;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
}

.tool-log-entry:last-child {
    border-bottom: none;
}

.log-time {
    color: #86868b;
    margin-right: 12px;
    font-size: 12px;
}

.log-content {
    flex-grow: 1;
}

/* Agent标签样式 */
.agent-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 8px;
    min-width: 90px;
    text-align: center;
}

.agent-planner { background: #007AFF20; color: #007AFF; }
.agent-fundamental { background: #34C75920; color: #34C759; }
.agent-technical { background: #FF954020; color: #FF9540; }
.agent-valuation { background: #AF52DE20; color: #AF52DE; }
.agent-news { background: #FF2D5520; color: #FF2D55; }
.agent-summarizer { background: #5856D620; color: #5856D6; }
.agent-system { background: #8E8E9320; color: #8E8E93; }

/* 状态标记 */
.status-tag {
    font-size: 11px;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 8px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}

.status-running { 
    background: #FFD60A20; 
    color: #FFD60A; 
}

.status-running::before {
    content: "⟳";
    font-weight: bold;
    display: inline-block;
    animation: spin 1s linear infinite;
}

.status-done { background: #34C75920; color: #34C759; }

/* 下载按钮 */
.stDownloadButton > button {
    background: #1d1d1f !important;
    color: white !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover {
    background: #333 !important;
}

/* 分隔线 */
.apple-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #d2d2d7, transparent);
    margin: 32px 0;
}

/* Expander样式 */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.5) !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)


# 节点进度映射
# Start: 节点开始时的基础进度
# End: 节点完成时的进度
NODE_PROGRESS = {
    'planner': {'start': 0, 'end': 10, 'label': '🎯 任务规划', 'desc': '分析用户意图...'},
    'fundamental': {'start': 10, 'end': 30, 'label': '💰 基本面分析', 'desc': '分析财报数据...'},
    'technical': {'start': 30, 'end': 50, 'label': '📉 技术面分析', 'desc': '分析K线走势...'},
    'valuation': {'start': 50, 'end': 70, 'label': '💹 估值分析', 'desc': '计算合理估值...'},
    'news': {'start': 70, 'end': 90, 'label': '📰 新闻分析', 'desc': '评估市场情绪...'},
    'summarizer': {'start': 90, 'end': 100, 'label': '📝 生成报告', 'desc': '撰写最终报告...'},
}

async def run_analysis_async(query, status_container, progress_bar, log_container):
    """异步运行分析工作流，实时捕获事件"""
    try:
        graph = create_stock_analysis_graph_v2()
        
        initial_state = {
            'user_query': query,
            'messages': []
        }
        
        # logs 存储结构化数据: {'node': str, 'status': str, 'html': str}
        logs_data = []
        final_state = {}
        
        current_node = None
        current_progress = 0
        
        def render_logs():
            """渲染所有日志"""
            full_html = "".join([item['html'] for item in logs_data])
            log_container.markdown(
                f'<div class="tool-log">{full_html}</div>',
                unsafe_allow_html=True
            )

        def update_log(node, message, status="info"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            badge_class = f"agent-{node}" if node in NODE_PROGRESS else "agent-system"
            
            status_html = ""
            if status == "running":
                status_html = '<span class="status-tag status-running">RUNNING</span>'
            elif status == "done":
                status_html = '<span class="status-tag status-done">DONE</span>'
                
            log_html = textwrap.dedent(f'''
            <div class="tool-log-entry">
                <span class="log-time">{timestamp}</span>
                <span class="agent-badge {badge_class}">{node.upper()}</span>
                <span class="log-content">{message}</span>
                {status_html}
            </div>
            ''')
            
            # 如果是Done状态，查找上一个该节点的Running状态并替换
            if status == "done":
                found = False
                for i in range(len(logs_data) - 1, -1, -1):
                    if logs_data[i]['node'] == node and logs_data[i]['status'] == 'running':
                        logs_data[i] = {
                            'node': node,
                            'status': 'done',
                            'html': log_html
                        }
                        found = True
                        break
                if not found:
                    logs_data.append({'node': node, 'status': status, 'html': log_html})
            else:
                logs_data.append({'node': node, 'status': status, 'html': log_html})
            
            render_logs()

        # 订阅事件流
        async for event in graph.astream_events(initial_state, version="v1"):
            kind = event["event"]
            name = event["name"]
            data = event["data"]
            
            # 1. 节点开始 (on_chain_start)
            if kind == "on_chain_start" and name in NODE_PROGRESS:
                current_node = name
                node_info = NODE_PROGRESS[name]
                
                # 更新进度条
                current_progress = node_info['start']
                progress_bar.progress(current_progress)
                
                # 更新状态文本
                status_container.markdown(textwrap.dedent(f"""
                <div class="status-text">
                    <span class="status-icon">🚀</span>
                    <strong>{node_info['label']}</strong> - {node_info['desc']}
                </div>
                """), unsafe_allow_html=True)
                
                update_log(name, "开始执行...", "running")
            
            # 2. 节点完成 (on_chain_end)
            elif kind == "on_chain_end":
                if name in NODE_PROGRESS:
                    node_info = NODE_PROGRESS[name]
                    current_progress = node_info['end']
                    progress_bar.progress(current_progress)
                    update_log(name, "执行完成", "done")
                
                # 捕获状态更新
                if "output" in data and isinstance(data["output"], dict):
                    final_state.update(data["output"])

            # 3. 工具调用开始 (on_tool_start)
            elif kind == "on_tool_start":
                if current_progress < 95:
                    progress_bar.progress(current_progress + 2)
                
                update_log(current_node or "system", f"调用工具: {name}", "running")
                
            # 4. 工具调用结束 (on_tool_end)
            elif kind == "on_tool_end":
                update_log(current_node or "system", f"工具 {name} 返回结果", "done")

        # 完成
        progress_bar.progress(100)
        status_container.markdown(textwrap.dedent("""
        <div class="status-text">
            <span class="status-icon">✅</span>
            <strong>分析完成</strong> - 报告已生成
        </div>
        """), unsafe_allow_html=True)
        
        return final_state
        
    except Exception as e:
        status_container.error(f"分析出错: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None


def main():
    # 标题区
    st.markdown('<div class="apple-title">📈 Agentic Stock Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="apple-subtitle">基于多Agent协作的智能股票分析系统</div>', unsafe_allow_html=True)

    # 状态检查
    if not config.OPENAI_API_KEY:
        st.warning("⚠️ 未检测到 OPENAI_API_KEY，请检查 .env 配置")
    
    # 输入区 - 使用form支持回车提交
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    with st.form(key="analysis_form", clear_on_submit=False):
        col1, col2 = st.columns([4, 1])
        with col1:
            query = st.text_input(
                "请输入您想分析的股票或问题",
                placeholder="例如：分析贵州茅台的投资价值",
                label_visibility="collapsed",
                key="stock_query"
            )
        with col2:
            submit_btn = st.form_submit_button("🚀 开始分析", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 分析逻辑
    if submit_btn and query:
        st.markdown('<div class="apple-divider"></div>', unsafe_allow_html=True)
        
        # 创建进度显示区域
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔄 分析进度")
        
        progress_bar = st.progress(0)
        status_container = st.empty()
        
        # 日志显示区域 (默认展开)
        with st.expander("📋 实时分析日志", expanded=True):
            log_container = st.empty()
            log_container.markdown('<div class="tool-log">等待分析任务启动...</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 运行异步分析
        result = asyncio.run(run_analysis_async(query, status_container, progress_bar, log_container))
        
        if result:
            st.markdown('<div class="apple-divider"></div>', unsafe_allow_html=True)
            
            # 结果展示区
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            stock_info = f"{result.get('company_name', '未知')} ({result.get('stock_code', '未知')})"
            st.markdown(f"### 📊 {stock_info} 分析报告")
            
            # 报告下载
            if result.get('final_report'):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    filename = f"Report_{result.get('company_name', 'stock')}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    st.download_button(
                        label="📥 下载 Markdown 报告",
                        data=result['final_report'],
                        file_name=filename,
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                st.markdown('<div class="apple-divider"></div>', unsafe_allow_html=True)
                
                # 报告展示
                st.markdown(result['final_report'])
            else:
                st.error("无法生成报告，请检查日志。")
            
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
