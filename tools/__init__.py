"""
工具层模块
包含所有MCP工具函数
"""

from .stock_market import (
    get_historical_k_data,
    get_stock_basic_info,
    get_dividend_data,
    get_adjust_factor_data,
)
from .financial_reports import (
    get_profit_data,
    get_operation_data,
    get_growth_data,
    get_balance_data,
    get_cash_flow_data,
    get_dupont_data,
    get_performance_express_report,
    get_forecast_report,
)
from .indices import (
    get_stock_industry,
    get_sz50_stocks,
    get_hs300_stocks,
    get_zz500_stocks,
)
from .market_overview import (
    get_trade_dates,
    get_all_stock,
)
from .date_utils import (
    get_latest_trading_date,
    get_market_analysis_timeframe,
)
from .news_crawler import crawl_news
from .stock_search import query_stock_info

__all__ = [
    # 股票市场
    "get_historical_k_data",
    "get_stock_basic_info", 
    "get_dividend_data",
    "get_adjust_factor_data",
    # 财务报表
    "get_profit_data",
    "get_operation_data",
    "get_growth_data",
    "get_balance_data",
    "get_cash_flow_data",
    "get_dupont_data",
    "get_performance_express_report",
    "get_forecast_report",
    # 指数
    "get_stock_industry",
    "get_sz50_stocks",
    "get_hs300_stocks",
    "get_zz500_stocks",
    # 市场概览
    "get_trade_dates",
    "get_all_stock",
    # 日期工具
    "get_latest_trading_date",
    "get_market_analysis_timeframe",
    # 新闻
    "crawl_news",
    # 股票查询
    "query_stock_info",
]
