"""
任务规划Agent
负责解析用户查询，识别意图，提取公司名称，查询股票代码
支持三分支路由：股票分析 / 公司内部知识 / 通用问答
"""
import json
import re
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from .base_agent import BaseAgent
from prompts.planner import PLANNER_PROMPT
from tools.stock_search import query_stock_info


class PlannerAgent(BaseAgent):
    """任务规划Agent - 支持意图路由"""
    
    # 意图关键词
    INTENT_KEYWORDS = {
        "stock": [
            "分析", "股票", "投资", "估值", "行情", "K线", "基本面", "技术面",
            "市盈率", "PE", "PB", "ROE", "财报", "年报", "研报", "股价",
            "买入", "卖出", "持有", "涨", "跌", "茅台", "五粮液"
        ],
        "company": [
            "例会", "手册", "规章", "请假", "公司介绍", "流程", "制度",
            "员工", "部门", "考勤", "报销", "审批", "OA", "内部"
        ],
    }
    
    def __init__(self):
        super().__init__(
            name="任务规划Agent",
            tools=[query_stock_info],
            system_prompt=PLANNER_PROMPT
        )
    
    def _classify_intent_with_llm(self, query: str) -> str:
        """
        使用 LLM 进行意图分类（语义理解）
        
        Args:
            query: 用户查询
        
        Returns:
            意图: "stock" | "company" | "general"
        """
        prompt = f"""请判断以下用户查询的意图类型，只返回一个单词。

**意图类型定义**：
- stock: 股票投资分析相关（如：分析某公司、查看股价、了解财报等）
- company: 公司内部知识查询（如：请假流程、报销制度、员工手册等）
- general: 通用问答（如：天气、常识、技术问题等）

**用户查询**：{query}

**意图类型**："""
        
        try:
            print(f"    [Planner] 关键词未匹配，调用LLM进行语义理解...")
            response = self.llm.invoke([HumanMessage(content=prompt)])
            intent = response.content.strip().lower()
            
            # 验证返回值
            if intent in ['stock', 'company', 'general']:
                print(f"    [Planner] LLM分类结果: {intent}")
                return intent
            else:
                print(f"    [Planner] LLM返回无效值: {intent}, 默认为general")
                return 'general'
        except Exception as e:
            print(f"    [Planner] LLM分类失败: {e}, 默认为general")
            return 'general'
    
    def _classify_intent(self, query: str) -> str:
        """
        混合意图识别：优先关键词，回退 LLM
        
        Args:
            query: 用户查询
        
        Returns:
            意图: "stock" | "company" | "general"
        """
        query_lower = query.lower()
        
        # 第1步：快速关键词匹配 - stock
        for keyword in self.INTENT_KEYWORDS["stock"]:
            if keyword.lower() in query_lower:
                print(f"    [Planner] 关键词匹配 '{keyword}' -> stock")
                return "stock"
        
        # 第2步：快速关键词匹配 - company
        for keyword in self.INTENT_KEYWORDS["company"]:
            if keyword.lower() in query_lower:
                print(f"    [Planner] 关键词匹配 '{keyword}' -> company")
                return "company"
        
        # 第3步：关键词未匹配，调用 LLM 进行语义理解
        print(f"    [Planner] 关键词匹配失败")
        return self._classify_intent_with_llm(query)
    
    def run(self, state: dict) -> dict:
        """
        运行任务规划
        
        Args:
            state: 包含user_query的状态
        
        Returns:
            更新后的状态，包含intent, company_name, stock_code, market
        """
        user_query = state.get('user_query', '')
        
        # 1. 意图识别
        intent = self._classify_intent(user_query)
        print(f"    [Planner] 意图识别: {intent}")
        
        # 2. 非股票分析直接返回
        if intent != "stock":
            return {
                **state,
                'intent': intent,
                'company_name': '',
                'stock_code': '',
                'market': '',
                'messages': []
            }
        
        # 3. 股票分析：提取公司和代码
        prompt = PLANNER_PROMPT.format(user_query=user_query)
        messages = [HumanMessage(content=prompt)]
        
        # 调用Agent
        result = self.invoke({'messages': messages})
        
        # 解析结果
        ai_message = result['messages'][-1]
        response_text = ai_message.content if hasattr(ai_message, 'content') else str(ai_message)
        
        # 尝试从响应中提取JSON
        company_name = ""
        stock_code = ""
        market = ""
        
        # 调试: 打印原始响应
        print(f"    [DEBUG] Planner原始响应: {response_text[:500]}...")
        
        try:
            # 方法1: 尝试从 Markdown 代码块中提取 JSON
            json_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
            if json_block_match:
                json_str = json_block_match.group(1)
                print(f"    [DEBUG] 从代码块提取JSON: {json_str[:200]}...")
                data = json.loads(json_str)
                company_name = data.get('company_name', '')
                stock_code = data.get('stock_code', '')
                market = data.get('market', '')
            else:
                # 方法2: 尝试匹配裸 JSON 对象 (允许嵌套)
                json_match = re.search(r'\{[^{}]*"company_name"\s*:\s*"[^"]*"[^{}]*\}', response_text, re.DOTALL)
                if json_match:
                    print(f"    [DEBUG] 从文本提取JSON: {json_match.group()[:200]}...")
                    data = json.loads(json_match.group())
                    company_name = data.get('company_name', '')
                    stock_code = data.get('stock_code', '')
                    market = data.get('market', '')
        except json.JSONDecodeError as e:
            print(f"    [DEBUG] JSON解析失败: {e}")
        
        # 如果JSON解析失败，尝试从文本中提取股票代码
        if not stock_code:
            # 尝试匹配股票代码格式
            code_match = re.search(r'(sh\.\d{6}|sz\.\d{6}|hk\.\d{5})', response_text, re.IGNORECASE)
            if code_match:
                stock_code = code_match.group(1).lower()
                print(f"    [DEBUG] 从文本提取股票代码: {stock_code}")
        
        print(f"    [DEBUG] 解析结果: company={company_name}, code={stock_code}, market={market}")
        
        # 特殊处理：如果意图是 stock 但没找到股票代码
        # 这通常意味着是通用问题（如"分析过哪些行业"）或历史查询
        if intent == "stock" and not stock_code:
            print(f"    [Planner] ⚠️  未识别到股票代码，降级为通用问答(general)")
            return {
                **state,
                'intent': 'general',  # 修改意图
                'company_name': '',
                'stock_code': '',
                'market': '',
                'messages': []
            }
        
        return {
            **state,
            'intent': intent,
            'company_name': company_name,
            'stock_code': stock_code,
            'market': market,
            'messages': result['messages']
        }
