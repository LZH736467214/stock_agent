"""
股票市场工具模块
提供股票市场相关数据获取功能
"""
from typing import Optional, List
from langchain_core.tools import tool
from .baostock_utils import fetch_generic_data, format_to_markdown


@tool
def get_historical_k_data(
    code: str,
    start_date: str,
    end_date: str,
    frequency: str = "d",
    adjustflag: str = "3",
    fields: str = "date,open,high,low,close,volume,amount,turn,pctChg"
) -> str:
    """
    获取股票历史K线数据
    
    Args:
        code: 股票代码，如 sh.600519 (贵州茅台)
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        frequency: K线频率，d=日线, w=周线, m=月线
        adjustflag: 复权类型，1=后复权, 2=前复权, 3=不复权
        fields: 返回字段，如 date,open,high,low,close,volume
    
    Returns:
        str: Markdown格式的K线数据表格
    """
    try:
        df = fetch_generic_data(
            query_type='k_data',
            code=code,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            adjustflag=adjustflag,
            fields=fields
        )
        return format_to_markdown(df, f"{code} K线数据 ({start_date} 至 {end_date})")
    except Exception as e:
        return f"获取K线数据失败: {str(e)}"


@tool
def get_stock_basic_info(code: str) -> str:
    """
    获取股票基本信息
    
    Args:
        code: 股票代码，如 sh.600519 (贵州茅台)
    
    Returns:
        str: Markdown格式的股票基本信息
    """
    try:
        df = fetch_generic_data(query_type='stock_basic', code=code)
        return format_to_markdown(df, f"{code} 基本信息")
    except Exception as e:
        return f"获取股票基本信息失败: {str(e)}"


@tool
def get_dividend_data(
    code: str,
    year: str,
    year_type: str = "report"
) -> str:
    """
    获取股票分红派息数据
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份，如 2023
        year_type: 年份类型，report=预案公告年份, operate=除权除息年份
    
    Returns:
        str: Markdown格式的分红数据
    """
    try:
        df = fetch_generic_data(
            query_type='dividend',
            code=code,
            year=year,
            year_type=year_type
        )
        return format_to_markdown(df, f"{code} {year}年分红数据")
    except Exception as e:
        return f"获取分红数据失败: {str(e)}"


@tool
def get_adjust_factor_data(
    code: str,
    start_date: str,
    end_date: str
) -> str:
    """
    获取股票复权因子数据
    
    Args:
        code: 股票代码，如 sh.600519
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的复权因子数据
    """
    try:
        df = fetch_generic_data(
            query_type='adjust_factor',
            code=code,
            start_date=start_date,
            end_date=end_date
        )
        return format_to_markdown(df, f"{code} 复权因子数据")
    except Exception as e:
        return f"获取复权因子数据失败: {str(e)}"
