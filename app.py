"""
多Agent股票顾问系统 - Web界面 (Streamlit)
Apple Design Language 风格 - 适配三分支路由 (Stock/Company/General)
"""
import streamlit as st
import asyncio
import textwrap
import json
from datetime import datetime
from graph.workflow import create_multi_branch_graph
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
    transition: transform 0.2s ease;
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
    display: flex;
    align-items: center;
    gap: 8px;
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
    border: 1px solid rgba(255,255,255,0.1);
}

.tool-log-entry {
    padding: 8px 0;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
}

.tool-log-entry:last-child { border-bottom: none; }

.log-time {
    color: #86868b;
    margin-right: 12px;
    font-size: 11px;
    min-width: 50px;
}

.log-content { flex-grow: 1; margin-left: 8px; }

/* Agent标签样式 */
.agent-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
    min-width: 90px;
    text-align: center;
    text-transform: uppercase;
}

.agent-planner { background: #007AFF20; color: #007AFF; }
.agent-fundamental { background: #34C75920; color: #34C759; }
.agent-technical { background: #FF954020; color: #FF9540; }
.agent-valuation { background: #AF52DE20; color: #AF52DE; }
.agent-news { background: #FF2D5520; color: #FF2D55; }
.agent-summarizer { background: #5856D620; color: #5856D6; }
.agent-system { background: #8E8E9320; color: #8E8E93; }
.agent-company_qa { background: #FF9F0A20; color: #FF9F0A; } /* Orange */
.agent-general_qa { background: #30B0C720; color: #30B0C7; } /* Teal */

/* 状态标记 */
.status-tag {
    font-size: 10px;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 8px;
    font-weight: 700;
}

@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }

.status-running { background: #FFD60A20; color: #FFD60A; }
.status-running::before {
    content: "⟳";
    display: inline-block;
    animation: spin 1s linear infinite;
    margin-right: 4px;
}
.status-done { background: #34C75920; color: #34C759; }

/* 报告结果样式 */
.report-container {
    padding: 20px;
}

.report-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
}

.report-icon {
    font-size: 2rem;
    margin-right: 12px;
}

.report-title {
    font-size: 1.5rem;
    font-weight: 700;
}

/* 分隔线 */
.apple-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, #d2d2d7, transparent);
    margin: 32px 0;
}
</style>
""", unsafe_allow_html=True)


# 节点进度与元数据映射
NODE_METADATA = {
    'planner': {'start': 0, 'end': 10, 'label': '🎯 意图识别', 'desc': '分析用户查询意图...'},
    
    # 股票分支
    'fundamental': {'start': 10, 'end': 30, 'label': '💰 基本面分析', 'desc': '分析财报与运营数据...'},
    'technical': {'start': 30, 'end': 50, 'label': '📉 技术面分析', 'desc': '计算技术指标与趋势...'},
    'valuation': {'start': 50, 'end': 70, 'label': '💹 估值分析', 'desc': '进行相对与绝对估值...'},
    'news': {'start': 70, 'end': 90, 'label': '📰 新闻分析', 'desc': '抓取并分析市场舆情...'},
    'summarizer': {'start': 90, 'end': 100, 'label': '📝 生成报告', 'desc': 'RAG 检索与报告生成...'},
    
    # 公司知识分支
    'company_qa': {'start': 50, 'end': 90, 'label': '🏢 知识检索', 'desc': '查询公司内部知识库...'},
    
    # 通用分支
    'general_qa': {'start': 50, 'end': 90, 'label': '🤖 智能问答', 'desc': '思考并生成回答...'},
}

async def run_analysis_async(query, status_container, progress_bar, log_container):
    """异步运行分析工作流"""
    try:
        # 使用三分支工作流
        graph = create_multi_branch_graph()
        
        initial_state = {
            'user_query': query,
            'messages': []
        }
        
        # 日志数据存储
        logs_data = []
        final_state = {}
        
        current_node = None
        current_progress = 0
        detected_intent = None
        
        def render_logs():
            """渲染日志HTML"""
            full_html = "".join([item['html'] for item in logs_data])
            log_container.markdown(
                f'<div class="tool-log">{full_html}</div>',
                unsafe_allow_html=True
            )

        def update_log(node, message, status="info"):
            timestamp = datetime.now().strftime("%H:%M:%S")
            badge_class = f"agent-{node}" if node in NODE_METADATA else "agent-system"
            
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
            
            # 更新已存在的Running状态为Done
            if status == "done":
                for i in range(len(logs_data) - 1, -1, -1):
                    if logs_data[i]['node'] == node and logs_data[i]['status'] == 'running':
                        logs_data[i] = {'node': node, 'status': 'done', 'html': log_html}
                        render_logs()
                        return

            logs_data.append({'node': node, 'status': status, 'html': log_html})
            render_logs()

        # 订阅事件流
        async for event in graph.astream_events(initial_state, version="v1"):
            kind = event["event"]
            name = event["name"]
            data = event["data"]
            
            # 1. 节点开始
            if kind == "on_chain_start" and name in NODE_METADATA:
                current_node = name
                node_info = NODE_METADATA[name]
                
                # 智能跳转进度：如果刚识别完意图，根据 intent 跳转
                if name == 'planner':
                    current_progress = 5
                else:
                    current_progress = node_info['start']
                
                progress_bar.progress(current_progress)
                
                # 更新状态卡片
                status_container.markdown(textwrap.dedent(f"""
                <div class="status-text">
                    <span class="status-icon">🚀</span>
                    <div>
                        <strong>{node_info['label']}</strong><br>
                        <span style="font-size: 13px; color: #86868b;">{node_info['desc']}</span>
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
                update_log(name, "开始执行工作...", "running")
            
            # 2. 节点结束
            elif kind == "on_chain_end":
                if name in NODE_METADATA:
                    node_info = NODE_METADATA[name]
                    current_progress = node_info['end']
                    progress_bar.progress(current_progress)
                    update_log(name, "执行完成", "done")
                
                # 捕获状态输出
                if "output" in data and isinstance(data["output"], dict):
                    output = data["output"]
                    final_state.update(output)
                    
                    # 捕获意图识别结果
                    if name == "planner" and "intent" in output:
                        detected_intent = output["intent"]
                        intent_label = {
                            "stock": "📈 股票分析",
                            "company": "🏢 公司知识查询",
                            "general": "🤖 通用问答"
                        }.get(detected_intent, detected_intent)
                        
                        update_log("system", f"意图识别为: {intent_label}", "info")

            # 3. 工具调用
            elif kind == "on_tool_start":
                update_log(current_node or "system", f"调用工具: {name}", "running")
                
            elif kind == "on_tool_end":
                update_log(current_node or "system", f"工具返回结果", "done")

        # 完成
        progress_bar.progress(100)
        status_container.markdown(textwrap.dedent("""
        <div class="status-text">
            <span class="status-icon">✅</span>
            <strong>处理完成</strong>
        </div>
        """), unsafe_allow_html=True)
        
        # 补充结果状态
        final_state['detected_intent'] = detected_intent
        return final_state
        
    except Exception as e:
        status_container.error(f"处理出错: {str(e)}")
        # import traceback
        # st.error(traceback.format_exc())
        return None


def main():
    # 标题区
    st.markdown('<div class="apple-title">📈 Agentic Stock Advisor</div>', unsafe_allow_html=True)
    st.markdown('<div class="apple-subtitle">智能多意图股票助手 • 股票分析 | 公司知识 | 通用问答</div>', unsafe_allow_html=True)

    # 状态检查
    if not config.OPENAI_API_KEY:
        st.warning("⚠️ 未检测到 OPENAI_API_KEY，请检查 .env 配置")
    
    # 输入区
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    with st.form(key="analysis_form", clear_on_submit=False):
        col1, col2 = st.columns([5, 1])
        with col1:
            query = st.text_input(
                "输入",
                placeholder="例如：'分析茅台' 或 '公司请假流程' 或 '什么是人工智能'",
                label_visibility="collapsed",
                key="stock_query"
            )
        with col2:
            submit_btn = st.form_submit_button("🚀 发送", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 处逻辑
    if submit_btn and query:
        st.markdown('<div class="apple-divider"></div>', unsafe_allow_html=True)
        
        # 进度与日志区
        col_progress, col_log = st.columns([1, 1])
        
        with col_progress:
            st.markdown('<div class="glass-card" style="height: 100%;">', unsafe_allow_html=True)
            st.markdown("### 🔄 处理进度")
            progress_bar = st.progress(0)
            status_container = st.empty()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_log:
            with st.expander("📋 实时思考日志", expanded=True):
                log_container = st.empty()
                log_container.markdown('<div class="tool-log">等待任务启动...</div>', unsafe_allow_html=True)

        # 运行异步分析
        result = asyncio.run(run_analysis_async(query, status_container, progress_bar, log_container))
        
        if result:
            st.markdown('<div class="apple-divider"></div>', unsafe_allow_html=True)
            
            # 结果展示区
            intent = result.get('detected_intent', 'general')
            
            # 根据意图展示不同风格的头部
            if intent == 'stock':
                header_icon = "📊"
                header_title = f"{result.get('company_name', '股票')} 投资分析报告"
            elif intent == 'company':
                header_icon = "🏢"
                header_title = "公司知识查询结果"
            else:
                header_icon = "🤖"
                header_title = "智能问答结果"
                
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            
            # 头部
            col_h1, col_h2 = st.columns([1, 15])
            with col_h1:
                st.markdown(f"<div class='report-icon'>{header_icon}</div>", unsafe_allow_html=True)
            with col_h2:
                st.markdown(f"<div class='report-title'>{header_title}</div>", unsafe_allow_html=True)
                if intent == 'stock':
                    st.caption(f"代码: {result.get('stock_code', '--')} | 市场: {result.get('market', '--')}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 报告内容
            if result.get('final_report'):
                # 如果是股票报告，提供下载
                if intent == 'stock':
                    report_content = result['final_report']
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
                    filename = f"Report_{result.get('company_name', 'stock')}_{timestamp}.md"
                    
                    st.download_button(
                        label="📥 下载完整报告 (Markdown)",
                        data=report_content,
                        file_name=filename,
                        mime="text/markdown"
                    )
                    st.divider()
                
                st.markdown(result['final_report'])
            else:
                st.error("未生成有效内容，请检查日志。")
            
            st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
