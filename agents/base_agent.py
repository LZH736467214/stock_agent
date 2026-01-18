"""
Agent基类
提供ReAct Agent的基础实现
"""
from abc import ABC, abstractmethod
from typing import List, Any, Optional
from langchain_core.tools import BaseTool
from langchain_core.callbacks import BaseCallbackHandler
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import sys
import time
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import config


class LLMProgressCallback(BaseCallbackHandler):
    """LLM和工具调用进度回调，显示执行过程的提示"""
    
    def __init__(self, agent_name: str = "Agent"):
        self.agent_name = agent_name
        self.llm_call_count = 0
        self.tool_call_count = 0
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM开始调用时触发"""
        self.llm_call_count += 1
        current_time = time.strftime("%H:%M:%S")
        print(f"    💭 [{current_time}] [{self.agent_name}] 正在调用LLM分析 (第{self.llm_call_count}次)...", flush=True)
    
    def on_llm_end(self, response, **kwargs):
        """LLM调用结束时触发"""
        current_time = time.strftime("%H:%M:%S")
        print(f"    ✓  [{current_time}] [{self.agent_name}] LLM响应完成", flush=True)
    
    def on_tool_start(self, serialized, input_str, **kwargs):
        """工具开始调用时触发"""
        self.tool_call_count += 1
        tool_name = serialized.get("name", "未知工具")
        current_time = time.strftime("%H:%M:%S")
        print(f"    🔧 [{current_time}] [{self.agent_name}] 正在调用工具: {tool_name}...", flush=True)
    
    def on_tool_end(self, output, **kwargs):
        """工具调用结束时触发"""
        current_time = time.strftime("%H:%M:%S")
        output_len = len(str(output)) if output else 0
        print(f"    ✓  [{current_time}] [{self.agent_name}] 工具返回: {output_len} 字符", flush=True)


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(
        self,
        name: str,
        tools: List[BaseTool],
        system_prompt: str,
        model: Optional[str] = None
    ):
        """
        初始化Agent
        
        Args:
            name: Agent名称
            tools: 可用工具列表
            system_prompt: 系统提示词
            model: 使用的模型名称
        """
        self.name = name
        self.tools = tools
        self.system_prompt = system_prompt
        self.model = model or config.OPENAI_MODEL
        
        # 创建进度回调
        self.progress_callback = LLMProgressCallback(agent_name=name)
        
        # 创建LLM (添加超时配置和进度回调)
        self.llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=self.model,
            temperature=0,
            request_timeout=60,  # 60秒超时
            callbacks=[self.progress_callback],  # 添加LLM调用进度回调
        )
        
        # 创建ReAct Agent (如果有工具)
        if tools:
            self.agent = create_react_agent(
                model=self.llm,
                tools=tools,
                # 兼容性修复：移除modifier参数，改用SystemMessage
                # state_modifier=system_prompt  <- 旧版本
                # messages_modifier=system_prompt <- 新版本
            )
            # 设置递归限制 (防止无限循环)
            self.recursion_limit = 25  # 最多25次工具调用
        else:
            self.agent = None
            self.recursion_limit = 10
    
    def invoke(self, input_data: dict, debug: bool = False) -> dict:
        """
        执行Agent
        
        Args:
            input_data: 输入数据
            debug: 是否开启调试模式 (显示详细执行过程)
        
        Returns:
            执行结果
        """
        if self.agent:
            # 手动添加SystemMessage以兼容不同版本
            from langchain_core.messages import SystemMessage
            import time
            
            messages = input_data.get("messages", [])
            # 确保system_prompt作为第一条消息
            if self.system_prompt:
                system_msg = SystemMessage(content=self.system_prompt)
                # 检查是否已有SystemMessage
                if not messages or not isinstance(messages[0], SystemMessage):
                    messages = [system_msg] + messages
                
            # 使用ReAct Agent (带递归限制)
            input_data["messages"] = messages
            config_dict = {"recursion_limit": self.recursion_limit}
            
            if debug:
                # 调试模式：使用 stream 显示每一步
                print(f"\n    [DEBUG] 开始执行 {self.name}")
                print(f"    [DEBUG] 递归限制: {self.recursion_limit}")
                step_count = 0
                result = None
                
                for event in self.agent.stream(input_data, config=config_dict):
                    step_count += 1
                    current_time = time.strftime("%H:%M:%S")
                    
                    for key, value in event.items():
                        print(f"    [{current_time}] Step {step_count}: {key}")
                        
                        if key == "agent":
                            # LLM 响应
                            if "messages" in value:
                                for msg in value["messages"]:
                                    msg_type = type(msg).__name__
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        tool_names = [tc['name'] for tc in msg.tool_calls]
                                        print(f"        → LLM 决策: 调用工具 {tool_names}")
                                    elif hasattr(msg, 'content') and msg.content:
                                        content_preview = msg.content[:100].replace('\n', ' ')
                                        print(f"        → LLM 响应: {content_preview}...")
                        
                        elif key == "tools":
                            # 工具调用结果
                            if "messages" in value:
                                for msg in value["messages"]:
                                    if hasattr(msg, 'name'):
                                        content_len = len(msg.content) if hasattr(msg, 'content') else 0
                                        print(f"        → 工具 {msg.name} 返回: {content_len} 字符")
                        
                        result = value
                
                print(f"    [DEBUG] 执行完成，共 {step_count} 步")
                return result if result else {"messages": messages}
            else:
                # 正常模式 - 传递 callbacks 以显示工具调用进度
                config_dict["callbacks"] = [self.progress_callback]
                result = self.agent.invoke(input_data, config=config_dict)
                return result
        else:
            # 直接使用LLM
            messages = input_data.get('messages', [])
            response = self.llm.invoke(messages)
            return {'messages': messages + [response]}
    
    @abstractmethod
    def run(self, state: dict) -> dict:
        """
        运行Agent的主逻辑
        
        Args:
            state: 当前状态
        
        Returns:
            更新后的状态
        """
        pass
