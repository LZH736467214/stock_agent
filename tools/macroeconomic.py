"""
宏观经济工具模块
提供宏观经济相关数据获取功能
"""
from typing import Optional
from langchain_core.tools import tool
from .baostock_utils import fetch_macro_data, format_to_markdown


@tool
def get_deposit_rate_data(start_date: str, end_date: str) -> str:
    """
    获取基准存款利率数据
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的存款利率数据
    """
    try:
        df = fetch_macro_data('deposit_rate', start_date, end_date)
        return format_to_markdown(df, "基准存款利率")
    except Exception as e:
        return f"获取存款利率数据失败: {str(e)}"


@tool
def get_loan_rate_data(start_date: str, end_date: str) -> str:
    """
    获取基准贷款利率数据
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的贷款利率数据
    """
    try:
        df = fetch_macro_data('loan_rate', start_date, end_date)
        return format_to_markdown(df, "基准贷款利率")
    except Exception as e:
        return f"获取贷款利率数据失败: {str(e)}"


@tool
def get_required_reserve_ratio_data(start_date: str, end_date: str) -> str:
    """
    获取存款准备金率数据
    
    存款准备金率是央行用于控制市场货币量的工具
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的存款准备金率数据
    """
    try:
        df = fetch_macro_data('rrr', start_date, end_date)
        return format_to_markdown(df, "存款准备金率")
    except Exception as e:
        return f"获取存款准备金率数据失败: {str(e)}"


@tool
def get_money_supply_data_month(start_date: str, end_date: str) -> str:
    """
    获取月度货币供应量数据 (M0、M1、M2)
    
    - M0: 流通中的现金
    - M1: M0 + 活期存款
    - M2: M1 + 定期存款 + 储蓄存款
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的月度货币供应量数据
    """
    try:
        df = fetch_macro_data('money_supply_month', start_date, end_date)
        return format_to_markdown(df, "月度货币供应量")
    except Exception as e:
        return f"获取月度货币供应量数据失败: {str(e)}"


@tool
def get_money_supply_data_year(start_date: str, end_date: str) -> str:
    """
    获取年度货币供应量数据 (M0、M1、M2年末余额)
    
    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的年度货币供应量数据
    """
    try:
        df = fetch_macro_data('money_supply_year', start_date, end_date)
        return format_to_markdown(df, "年度货币供应量")
    except Exception as e:
        return f"获取年度货币供应量数据失败: {str(e)}"
