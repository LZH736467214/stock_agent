"""
财务报表工具模块
提供财务报表相关数据获取功能 (双数据源: AKShare + Baostock)
"""
from typing import Optional
from langchain_core.tools import tool
from .data_source import fetch_financial_data_dual, format_to_markdown, RateLimitError
from .baostock_utils import fetch_generic_data


@tool
def get_profit_data(code: str, year: int, quarter: int) -> str:
    """
    获取公司盈利能力数据
    
    包含: ROE(净资产收益率)、ROA(总资产收益率)、净利润率、毛利率等
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份，如 2023
        quarter: 季度 (1-4)
    
    Returns:
        str: Markdown格式的盈利能力数据
    """
    try:
        df = fetch_financial_data_dual(code, year, quarter, 'profit')
        return format_to_markdown(df, f"{code} {year}Q{quarter} 盈利能力数据")
    except Exception as e:
        return f"获取盈利能力数据失败: {str(e)}"


@tool
def get_operation_data(code: str, year: int, quarter: int) -> str:
    """
    获取公司营运能力数据
    
    包含: 应收账款周转率、存货周转率、总资产周转率等
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份
        quarter: 季度 (1-4)
    
    Returns:
        str: Markdown格式的营运能力数据
    """
    try:
        df = fetch_financial_data_dual(code, year, quarter, 'operation')
        return format_to_markdown(df, f"{code} {year}Q{quarter} 营运能力数据")
    except Exception as e:
        return f"获取营运能力数据失败: {str(e)}"


@tool
def get_growth_data(code: str, year: int, quarter: int) -> str:
    """
    获取公司成长能力数据
    
    包含: 营业收入同比增长率、净利润同比增长率、净资产同比增长率等
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份
        quarter: 季度 (1-4)
    
    Returns:
        str: Markdown格式的成长能力数据
    """
    try:
        df = fetch_financial_data_dual(code, year, quarter, 'growth')
        return format_to_markdown(df, f"{code} {year}Q{quarter} 成长能力数据")
    except Exception as e:
        return f"获取成长能力数据失败: {str(e)}"


@tool
def get_balance_data(code: str, year: int, quarter: int) -> str:
    """
    获取公司偿债能力/资产负债数据
    
    包含: 流动比率、速动比率、资产负债率、权益乘数等
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份
        quarter: 季度 (1-4)
    
    Returns:
        str: Markdown格式的偿债能力数据
    """
    try:
        df = fetch_financial_data_dual(code, year, quarter, 'balance')
        return format_to_markdown(df, f"{code} {year}Q{quarter} 偿债能力数据")
    except Exception as e:
        return f"获取偿债能力数据失败: {str(e)}"


@tool
def get_cash_flow_data(code: str, year: int, quarter: int) -> str:
    """
    获取公司现金流量数据
    
    包含: 经营活动现金流、投资活动现金流、筹资活动现金流等
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份
        quarter: 季度 (1-4)
    
    Returns:
        str: Markdown格式的现金流量数据
    """
    try:
        df = fetch_financial_data_dual(code, year, quarter, 'cash_flow')
        return format_to_markdown(df, f"{code} {year}Q{quarter} 现金流量数据")
    except Exception as e:
        return f"获取现金流量数据失败: {str(e)}"


@tool
def get_dupont_data(code: str, year: int, quarter: int) -> str:
    """
    获取公司杜邦分析数据
    
    杜邦分析将ROE分解为: 净利润率 × 总资产周转率 × 权益乘数
    用于深入分析公司赚钱的秘诀
    
    Args:
        code: 股票代码，如 sh.600519
        year: 年份
        quarter: 季度 (1-4)
    
    Returns:
        str: Markdown格式的杜邦分析数据
    """
    try:
        df = fetch_financial_data_dual(code, year, quarter, 'dupont')
        return format_to_markdown(df, f"{code} {year}Q{quarter} 杜邦分析数据")
    except Exception as e:
        return f"获取杜邦分析数据失败: {str(e)}"


@tool
def get_performance_express_report(
    code: str,
    start_date: str,
    end_date: str
) -> str:
    """
    获取业绩快报数据
    
    业绩快报是正式财报发布前的简化版财报，包括营业收入、净利润、每股收益等
    
    Args:
        code: 股票代码，如 sh.600519
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的业绩快报数据
    """
    try:
        df = fetch_generic_data(
            query_type='performance_express',
            code=code,
            start_date=start_date,
            end_date=end_date
        )
        return format_to_markdown(df, f"{code} 业绩快报 ({start_date} 至 {end_date})")
    except Exception as e:
        return f"获取业绩快报数据失败: {str(e)}"


@tool
def get_forecast_report(
    code: str,
    start_date: str,
    end_date: str
) -> str:
    """
    获取业绩预告数据
    
    业绩预告基于当前经营情况预估未来表现，包含预期净利润、增长幅度等
    
    Args:
        code: 股票代码，如 sh.600519
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
    
    Returns:
        str: Markdown格式的业绩预告数据
    """
    try:
        df = fetch_generic_data(
            query_type='forecast',
            code=code,
            start_date=start_date,
            end_date=end_date
        )
        return format_to_markdown(df, f"{code} 业绩预告 ({start_date} 至 {end_date})")
    except Exception as e:
        return f"获取业绩预告数据失败: {str(e)}"
