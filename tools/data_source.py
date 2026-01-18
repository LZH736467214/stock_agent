"""
双数据源工具模块
优先使用 AKShare，失败时回退到 Baostock
"""
import pandas as pd
from typing import Optional, Tuple
import time
import threading

# 全局数据获取锁，防止多线程并发导致的 Baostock 崩溃或 Akshare 输出混乱
DATA_FETCH_LOCK = threading.Lock()


class DataSourceError(Exception):
    """数据源错误"""
    pass


class RateLimitError(DataSourceError):
    """请求频率限制错误"""
    pass


def _convert_stock_code(code: str, to_format: str = "akshare") -> str:
    """
    转换股票代码格式
    
    Args:
        code: 股票代码 (baostock格式: sh.600519 或 sz.000001)
        to_format: 目标格式 ("akshare" 或 "baostock")
    
    Returns:
        转换后的代码
    """
    if to_format == "akshare":
        # baostock format: sh.600519 -> akshare format: 600519
        if "." in code:
            return code.split(".")[1]
        return code
    else:
        # akshare format: 600519 -> baostock format: sh.600519
        code = code.replace(".", "")
        if code.startswith("6"):
            return f"sh.{code}"
        else:
            return f"sz.{code}"


def _fetch_from_akshare(
    code: str,
    data_type: str,
    year: int,
    quarter: int
) -> Tuple[bool, pd.DataFrame, str]:
    """
    从 AKShare 获取财务数据
    
    Returns:
        (成功标志, 数据DataFrame, 错误信息)
    """
    try:
        import akshare as ak
        
        ak_code = _convert_stock_code(code, "akshare")
        
        # 根据数据类型调用不同的 AKShare 接口
        if data_type == "profit":
            # 获取利润表数据
            df = ak.stock_lrb_em(symbol=ak_code)
            if df is not None and not df.empty:
                # 筛选指定季度
                # AKShare 返回的是累计数据，需要处理
                return True, df.head(4), ""
                
        elif data_type == "balance":
            # 获取资产负债表
            df = ak.stock_zcfz_em(symbol=ak_code)
            if df is not None and not df.empty:
                return True, df.head(4), ""
                
        elif data_type == "cash_flow":
            # 获取现金流量表
            df = ak.stock_xjll_em(symbol=ak_code)
            if df is not None and not df.empty:
                return True, df.head(4), ""
                
        elif data_type == "growth":
            # 获取成长能力指标
            df = ak.stock_financial_analysis_indicator(symbol=ak_code, start_year=str(year-1))
            if df is not None and not df.empty:
                return True, df.head(4), ""
                
        elif data_type == "operation":
            # 获取营运能力指标
            df = ak.stock_financial_analysis_indicator(symbol=ak_code, start_year=str(year-1))
            if df is not None and not df.empty:
                return True, df.head(4), ""
                
        elif data_type == "dupont":
            # 杜邦分析数据
            df = ak.stock_financial_analysis_indicator(symbol=ak_code, start_year=str(year-1))
            if df is not None and not df.empty:
                return True, df.head(4), ""
        
        return False, pd.DataFrame(), "AKShare 返回空数据"
        
    except Exception as e:
        error_msg = str(e)
        if "频繁" in error_msg or "limit" in error_msg.lower() or "rate" in error_msg.lower():
            return False, pd.DataFrame(), f"AKShare 请求频率受限: {error_msg}"
        return False, pd.DataFrame(), f"AKShare 错误: {error_msg}"


def _fetch_from_baostock(
    code: str,
    data_type: str,
    year: int,
    quarter: int
) -> Tuple[bool, pd.DataFrame, str]:
    """
    从 Baostock 获取财务数据 (备选方案)
    
    Returns:
        (成功标志, 数据DataFrame, 错误信息)
    """
    try:
        import baostock as bs
        from .baostock_utils import baostock_login_context
        
        func_map = {
            'profit': bs.query_profit_data,
            'operation': bs.query_operation_data,
            'growth': bs.query_growth_data,
            'balance': bs.query_balance_data,
            'cash_flow': bs.query_cash_flow_data,
            'dupont': bs.query_dupont_data,
        }
        
        if data_type not in func_map:
            return False, pd.DataFrame(), f"不支持的数据类型: {data_type}"
        
        with baostock_login_context():
            rs = func_map[data_type](code=code, year=year, quarter=quarter)
            
            if rs.error_code != '0':
                return False, pd.DataFrame(), f"Baostock 错误: {rs.error_msg}"
            
            data_list = []
            while rs.next():
                data_list.append(rs.get_row_data())
            
            if not data_list:
                return False, pd.DataFrame(), "Baostock 返回空数据"
                
            return True, pd.DataFrame(data_list, columns=rs.fields), ""
            
    except Exception as e:
        error_msg = str(e)
        if "接收数据异常" in error_msg or "list index" in error_msg:
            return False, pd.DataFrame(), f"Baostock 连接异常: {error_msg}"
        return False, pd.DataFrame(), f"Baostock 错误: {error_msg}"


def fetch_financial_data_dual(
    code: str,
    year: int,
    quarter: int,
    data_type: str,
    prefer_source: str = "baostock"
) -> pd.DataFrame:
    """
    双数据源财务数据获取
    
    优先使用 Baostock，失败时自动切换到 AKShare。
    两者都失败时抛出 RateLimitError。
    
    Args:
        code: 股票代码 (baostock格式: sh.600519)
        year: 年份
        quarter: 季度 (1-4)
        data_type: 数据类型 (profit/operation/growth/balance/cash_flow/dupont)
        prefer_source: 优先数据源 (默认 "baostock"，备选 "akshare")
    
    Returns:
        DataFrame: 财务数据
    
    Raises:
        RateLimitError: 当两个数据源都失败时
    """
    errors = []
    
    # 确定数据源顺序 (默认: Baostock 优先，AKShare 备选)
    if prefer_source == "baostock":
        sources = [
            ("Baostock", _fetch_from_baostock),
            ("AKShare", _fetch_from_akshare),
        ]
    else:
        sources = [
            ("AKShare", _fetch_from_akshare),
            ("Baostock", _fetch_from_baostock),
        ]
    
    # 依次尝试各数据源
    with DATA_FETCH_LOCK:
        for source_name, fetch_func in sources:
            success, df, error = fetch_func(code, data_type, year, quarter)
            
            if success and not df.empty:
                return df
            
            if error:
                errors.append(f"[{source_name}] {error}")
            
            # 切换数据源前短暂等待
            time.sleep(0.1)
    
    # 两个数据源都失败
    error_msg = "; ".join(errors)
    raise RateLimitError(
        f"数据获取失败，请求可能过于频繁，请稍后再试。\n详细错误: {error_msg}"
    )


def format_to_markdown(df: pd.DataFrame, title: str = "") -> str:
    """
    将DataFrame格式化为Markdown表格
    """
    if df.empty:
        return f"### {title}\n\n暂无数据\n" if title else "暂无数据\n"
    
    result = f"### {title}\n\n" if title else ""
    result += df.to_markdown(index=False)
    return result
