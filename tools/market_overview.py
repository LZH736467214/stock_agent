"""
市场概览工具模块
提供市场概览相关数据获取功能
"""
from typing import Optional
from langchain_core.tools import tool
from .baostock_utils import fetch_generic_data, format_to_markdown


@tool
def get_trade_dates(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> str:
    """
    获取交易日历数据
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的交易日数据
    """
    try:
        df = fetch_generic_data(
            query_type='trade_dates',
            start_date=start_date,
            end_date=end_date
        )
        return format_to_markdown(df, "交易日历")
    except Exception as e:
        return f"获取交易日历失败: {str(e)}"


@tool
def get_all_stock(date: Optional[str] = None) -> str:
    """
    获取指定日期的全市场股票列表
    
    Args:
        date: 日期 (YYYY-MM-DD)，如不提供则使用最新交易日
    
    Returns:
        str: Markdown格式的股票列表
    """
    try:
        df = fetch_generic_data(
            query_type='all_stock',
            date=date
        )
        # 限制返回数量避免过长
        if len(df) > 50:
            df = df.head(50)
            note = f"\n\n> 注：仅显示前50条记录，共{len(df)}条"
        else:
            note = ""
        return format_to_markdown(df, "全市场股票列表") + note
    except Exception as e:
        return f"获取股票列表失败: {str(e)}"
