"""
股票搜索工具模块
提供公司名称到股票代码的查询功能
"""
import baostock as bs
import pandas as pd
from typing import Optional, Dict, Any
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from .baostock_utils import baostock_login_context
import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import config


# 常用股票映射表 (公司简称 -> 股票代码)
STOCK_MAPPING = {
    # 白酒
    '贵州茅台': 'sh.600519',
    '茅台': 'sh.600519',
    '五粮液': 'sz.000858',
    '泸州老窖': 'sz.000568',
    '洋河股份': 'sz.002304',
    '山西汾酒': 'sh.600809',
    
    # 科技
    '腾讯': 'hk.00700',
    '阿里巴巴': 'hk.09988',
    '百度': 'hk.09888',
    '京东': 'hk.09618',
    '小米': 'hk.01810',
    '华为': None,  # 未上市
    
    # 银行
    '工商银行': 'sh.601398',
    '建设银行': 'sh.601939',
    '农业银行': 'sh.601288',
    '中国银行': 'sh.601988',
    '招商银行': 'sh.600036',
    
    # 新能源
    '宁德时代': 'sz.300750',
    '比亚迪': 'sz.002594',
    '隆基绿能': 'sh.601012',
    
    # 医药
    '恒瑞医药': 'sh.600276',
    '药明康德': 'sh.603259',
    '迈瑞医疗': 'sz.300760',
    
    # 互联网
    '美团': 'hk.03690',
    '网易': 'hk.09999',
    '快手': 'hk.01024',
    
    # 消费
    '伊利股份': 'sh.600887',
    '蒙牛乳业': 'hk.02319',
    '海天味业': 'sh.603288',
    '美的集团': 'sz.000333',
    '格力电器': 'sz.000651',
    
    # 保险
    '中国平安': 'sh.601318',
    '中国人寿': 'sh.601628',
    
    # 石油
    '中国石油': 'sh.601857',
    '中国石化': 'sh.600028',
}


def _search_stock_by_name(company_name: str) -> Optional[Dict[str, str]]:
    """
    通过公司名称搜索股票代码
    
    Args:
        company_name: 公司名称或简称
    
    Returns:
        包含股票信息的字典，或None
    """
    # 首先检查映射表
    if company_name in STOCK_MAPPING:
        code = STOCK_MAPPING[company_name]
        if code:
            return {'code': code, 'name': company_name, 'market': _get_market(code)}
        return None
    
    # 尝试从全市场股票中搜索
    try:
        with baostock_login_context():
            rs = bs.query_all_stock()
            if rs.error_code != '0':
                return None
            
            while rs.next():
                row = rs.get_row_data()
                stock_code = row[0]
                stock_name = row[1] if len(row) > 1 else ''
                
                if company_name in stock_name or stock_name in company_name:
                    return {
                        'code': stock_code,
                        'name': stock_name,
                        'market': _get_market(stock_code)
                    }
    except:
        pass
    
    return None


def _get_market(code: str) -> str:
    """
    根据股票代码判断市场
    """
    if code.startswith('sh.'):
        return 'A股-上海'
    elif code.startswith('sz.'):
        return 'A股-深圳'
    elif code.startswith('hk.'):
        return '港股'
    elif code.startswith('us.'):
        return '美股'
    return '未知'


def _extract_company_name_with_llm(query: str) -> str:
    """
    使用LLM从用户查询中提取公司名称
    
    Args:
        query: 用户查询
    
    Returns:
        提取的公司名称
    """
    prompt = f"""从以下查询中提取公司名称，只返回公司名称，不要其他内容。
如果查询中包含多个公司，只返回第一个。
如果没有明确的公司名称，返回"未识别"。

查询: {query}

公司名称:"""
    
    try:
        llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_MODEL,
            temperature=0
        )
        response = llm.invoke(prompt)
        return response.content.strip()
    except:
        return "未识别"


@tool
def query_stock_info(query: str) -> str:
    """
    查询股票信息
    根据用户输入的公司名称或查询语句，提取公司名称并查询对应的股票代码
    
    支持:
    - 直接输入公司名称: "贵州茅台"
    - 输入查询语句: "分析一下贵州茅台的投资价值"
    - 输入股票代码: "sh.600519"
    
    Args:
        query: 用户查询或公司名称
    
    Returns:
        str: 股票信息的Markdown格式文本
    """
    # 如果直接是股票代码格式
    if query.startswith(('sh.', 'sz.', 'hk.', 'us.')):
        try:
            with baostock_login_context():
                rs = bs.query_stock_basic(code=query)
                if rs.error_code == '0' and rs.next():
                    row = rs.get_row_data()
                    return f"""### 股票信息

| 项目 | 内容 |
|------|------|
| 股票代码 | {query} |
| 股票名称 | {row[1] if len(row) > 1 else '未知'} |
| 市场 | {_get_market(query)} |
| 状态 | 正常 |
"""
        except:
            pass
        return f"无法获取股票代码 {query} 的信息"
    
    # 首先尝试直接匹配
    result = _search_stock_by_name(query)
    
    # 如果直接匹配失败，使用LLM提取公司名称
    if not result:
        company_name = _extract_company_name_with_llm(query)
        if company_name and company_name != "未识别":
            result = _search_stock_by_name(company_name)
    
    if result:
        return f"""### 股票信息

| 项目 | 内容 |
|------|------|
| 公司名称 | {result['name']} |
| 股票代码 | {result['code']} |
| 市场 | {result['market']} |
| 状态 | 正常 |
"""
    
    return f"""### 股票查询结果

未找到与 "{query}" 相关的股票信息。

可能的原因:
1. 公司名称输入有误
2. 该公司尚未上市
3. 该公司不在支持的市场范围内 (目前支持: A股、港股)

请尝试使用完整的公司名称或股票代码重新查询。
"""
