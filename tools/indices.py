"""
指数工具模块
提供指数相关数据获取功能
"""
from typing import Optional
from langchain_core.tools import tool
from .baostock_utils import fetch_index_constituent_data, fetch_generic_data, format_to_markdown


@tool
def get_stock_industry(code: Optional[str] = None, date: Optional[str] = None) -> str:
    """
    获取股票行业分类数据
    
    Args:
        code: 股票代码，如 sh.600519。如不提供则返回所有股票的行业分类
        date: 日期 (YYYY-MM-DD)，如不提供则使用最新数据
    
    Returns:
        str: Markdown格式的行业分类数据
    """
    try:
        df = fetch_generic_data(
            query_type='stock_industry',
            code=code,
            date=date
        )
        title = f"{code} 行业分类" if code else "股票行业分类"
        return format_to_markdown(df, title)
    except Exception as e:
        return f"获取行业分类数据失败: {str(e)}"


@tool
def get_sz50_stocks(date: Optional[str] = None, limit: int = 20) -> str:
    """
    获取上证50指数成分股
    
    上证50 = 上海证券交易所最大的50家公司
    注意: 默认只返回前20只成分股以提高效率
    
    Args:
        date: 日期 (YYYY-MM-DD)，如不提供则使用最新数据
        limit: 返回的成分股数量上限，默认20
    
    Returns:
        str: Markdown格式的上证50成分股数据
    """
    try:
        df = fetch_index_constituent_data('sz50', date)
        if len(df) > limit:
            df = df.head(limit)
        return format_to_markdown(df, f"上证50成分股 (前{len(df)}只)")
    except Exception as e:
        return f"获取上证50成分股失败: {str(e)}"


@tool
def get_hs300_stocks(date: Optional[str] = None, limit: int = 40) -> str:
    """
    获取沪深300指数成分股（用于行业对标分析）
    
    沪深300 = 沪深两市最大的300家公司
    注意: 默认只返回前40只成分股以提高效率，如需更多可调整limit参数
    
    Args:
        date: 日期 (YYYY-MM-DD)，如不提供则使用最新数据
        limit: 返回的成分股数量上限，默认40（避免数据过多导致处理缓慢）
    
    Returns:
        str: Markdown格式的沪深300成分股数据（按权重排序的前limit只）
    """
    try:
        df = fetch_index_constituent_data('hs300', date)
        # 限制返回数量，避免LLM处理过多数据
        if len(df) > limit:
            df = df.head(limit)
        return format_to_markdown(df, f"沪深300成分股 (前{len(df)}只)")
    except Exception as e:
        return f"获取沪深300成分股失败: {str(e)}"


@tool
def get_zz500_stocks(date: Optional[str] = None, limit: int = 60) -> str:
    """
    获取中证500指数成分股
    
    中证500 = 中等规模的500家公司
    注意: 默认只返回前60只成分股以提高效率，如需更多可调整limit参数
    
    Args:
        date: 日期 (YYYY-MM-DD)，如不提供则使用最新数据
        limit: 返回的成分股数量上限，默认60（避免数据过多导致处理缓慢）
    
    Returns:
        str: Markdown格式的中证500成分股数据
    """
    try:
        df = fetch_index_constituent_data('zz500', date)
        if len(df) > limit:
            df = df.head(limit)
        return format_to_markdown(df, f"中证500成分股 (前{len(df)}只)")
    except Exception as e:
        return f"获取中证500成分股失败: {str(e)}"
