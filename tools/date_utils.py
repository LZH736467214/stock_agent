"""
日期工具模块
提供日期相关的工具函数
"""
from datetime import datetime, timedelta
from typing import Literal
import baostock as bs
from .baostock_utils import baostock_login_context


def get_latest_trading_date() -> str:
    """
    获取最新交易日
    如果当天是交易日则返回当天，否则返回最近的交易日
    
    Returns:
        str: 最新交易日期 (YYYY-MM-DD格式)
    """
    today = datetime.now()
    # 往前查找30天以确保找到交易日
    start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    
    with baostock_login_context():
        rs = bs.query_trade_dates(start_date=start_date, end_date=end_date)
        
        if rs.error_code != '0':
            raise RuntimeError(f"获取交易日失败: {rs.error_msg}")
        
        trading_dates = []
        while rs.next():
            row = rs.get_row_data()
            # is_trading_day字段为1表示交易日
            if row[1] == '1':
                trading_dates.append(row[0])
        
        if not trading_dates:
            raise RuntimeError("未找到交易日")
        
        return trading_dates[-1]


def get_market_analysis_timeframe(
    timeframe: Literal['recent', 'quarter', 'half_year', 'year', 'three_years'] = 'year'
) -> dict:
    """
    获取市场分析时间范围
    
    Args:
        timeframe: 时间范围类型
            - recent: 最近1个月
            - quarter: 最近1季度
            - half_year: 最近半年
            - year: 最近1年
            - three_years: 最近3年
    
    Returns:
        dict: 包含start_date和end_date的字典
    """
    end_date = datetime.now()
    
    timeframe_map = {
        'recent': timedelta(days=30),
        'quarter': timedelta(days=90),
        'half_year': timedelta(days=180),
        'year': timedelta(days=365),
        'three_years': timedelta(days=365 * 3),
    }
    
    if timeframe not in timeframe_map:
        raise ValueError(f"不支持的时间范围: {timeframe}")
    
    start_date = end_date - timeframe_map[timeframe]
    
    return {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'timeframe': timeframe,
        'description': f"从 {start_date.strftime('%Y-%m-%d')} 到 {end_date.strftime('%Y-%m-%d')}"
    }


def get_current_year_quarter() -> tuple:
    """
    获取当前年份和季度
    
    Returns:
        tuple: (year, quarter)
    """
    now = datetime.now()
    year = now.year
    month = now.month
    quarter = (month - 1) // 3 + 1
    
    # 如果当前季度还没结束，返回上一季度
    if month % 3 != 0:
        if quarter == 1:
            year -= 1
            quarter = 4
        else:
            quarter -= 1
    
    return year, quarter


def get_recent_quarters(n: int = 4) -> list:
    """
    获取最近n个季度
    
    Args:
        n: 季度数量
    
    Returns:
        list: [(year, quarter), ...] 列表
    """
    year, quarter = get_current_year_quarter()
    quarters = []
    
    for _ in range(n):
        quarters.append((year, quarter))
        if quarter == 1:
            year -= 1
            quarter = 4
        else:
            quarter -= 1
    
    return quarters
