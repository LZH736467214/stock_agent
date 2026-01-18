"""
Baostock数据源工具模块
提供与Baostock API交互的基础功能
"""
import baostock as bs
import pandas as pd
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import threading
import atexit


class BaostockConnectionManager:
    """
    Baostock 单例连接管理器
    使用线程锁确保线程安全，整个应用生命周期内只登录一次
    """
    _instance = None
    _lock = threading.Lock()
    _is_logged_in = False
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def login(self):
        """登录 Baostock (如果尚未登录)"""
        with self._lock:
            if not self._is_logged_in:
                login_result = bs.login()
                if login_result.error_code != '0':
                    raise ConnectionError(f"Baostock登录失败: {login_result.error_msg}")
                self._is_logged_in = True
                # 不再注册atexit，避免退出时卡住
    
    def logout(self):
        """登出 Baostock"""
        with self._lock:
            if self._is_logged_in:
                try:
                    bs.logout()
                except:
                    pass
                self._is_logged_in = False
    
    def ensure_connection(self):
        """确保已连接"""
        if not self._is_logged_in:
            self.login()


# 全局连接管理器实例
_connection_manager = BaostockConnectionManager()

# 全局查询锁，确保 Baostock 查询串行执行
QUERY_LOCK = threading.Lock()


@contextmanager
def baostock_login_context():
    """
    Baostock登录上下文管理器
    使用单例连接，不再每次都登录/登出
    """
    _connection_manager.ensure_connection()
    yield
    # 不再登出，保持连接


def ensure_baostock_connection():
    """确保 Baostock 连接可用"""
    _connection_manager.ensure_connection()


def fetch_financial_data(
    code: str,
    year: int,
    quarter: int,
    data_type: str
) -> pd.DataFrame:
    """
    通用财务数据获取函数
    
    Args:
        code: 股票代码 (如 sh.600519)
        year: 年份
        quarter: 季度 (1-4)
        data_type: 数据类型 (profit/operation/growth/balance/cash_flow/dupont)
    
    Returns:
        DataFrame: 财务数据
    """
    with baostock_login_context():
        # 整个查询操作都在锁内执行，避免死锁
        with QUERY_LOCK:
            func_map = {
                'profit': bs.query_profit_data,
                'operation': bs.query_operation_data,
                'growth': bs.query_growth_data,
                'balance': bs.query_balance_data,
                'cash_flow': bs.query_cash_flow_data,
                'dupont': bs.query_dupont_data,
            }
        
            if data_type not in func_map:
                raise ValueError(f"不支持的数据类型: {data_type}")
            
            rs = func_map[data_type](code=code, year=year, quarter=quarter)
            
            if rs.error_code != '0':
                raise RuntimeError(f"获取{data_type}数据失败: {rs.error_msg}")
            
            data_list = []
            max_rows = 10000  # 通用查询可能返回较多数据
            row_count = 0
            
            try:
                while rs.next() and row_count < max_rows:
                    row_data = rs.get_row_data()
                    data_list.append(row_data)
                    row_count += 1
            except Exception as e:
                # 捕获编码错误
                print(f"警告: 读取数据时出错 (已读取{row_count}条): {e}")
                if not data_list:
                    raise RuntimeError(f"读取数据失败: {e}")
            
            return pd.DataFrame(data_list, columns=rs.fields)


def fetch_index_constituent_data(
    index_type: str,
    date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取指数成分股数据
    
    Args:
        index_type: 指数类型 (sz50/hs300/zz500)
        date: 日期 (YYYY-MM-DD格式)
    
    Returns:
        DataFrame: 成分股数据
    """
    with baostock_login_context():
        func_map = {
            'sz50': bs.query_sz50_stocks,
            'hs300': bs.query_hs300_stocks,
            'zz500': bs.query_zz500_stocks,
        }
        
        if index_type not in func_map:
            raise ValueError(f"不支持的指数类型: {index_type}")
        
        if date:
            rs = func_map[index_type](date=date)
        else:
            rs = func_map[index_type]()
        
        if rs.error_code != '0':
            raise RuntimeError(f"获取{index_type}成分股失败: {rs.error_msg}")
        
        data_list = []
        max_rows = 500  # 防止无限循环，最多读取500条
        row_count = 0
        
        try:
            while rs.next() and row_count < max_rows:
                row_data = rs.get_row_data()
                data_list.append(row_data)
                row_count += 1
        except Exception as e:
            # 捕获编码错误或数据损坏
            print(f"警告: 读取成分股数据时出错 (已读取{row_count}条): {e}")
            if not data_list:
                raise RuntimeError(f"读取成分股数据失败: {e}")
        
        return pd.DataFrame(data_list, columns=rs.fields)


def fetch_macro_data(
    data_type: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    获取宏观经济数据
    
    Args:
        data_type: 数据类型 (deposit_rate/loan_rate/rrr/money_supply_month/money_supply_year)
        start_date: 开始日期
        end_date: 结束日期
    
    Returns:
        DataFrame: 宏观经济数据
    """
    with baostock_login_context():
        if data_type == 'deposit_rate':
            rs = bs.query_deposit_rate_data(start_date=start_date, end_date=end_date)
        elif data_type == 'loan_rate':
            rs = bs.query_loan_rate_data(start_date=start_date, end_date=end_date)
        elif data_type == 'rrr':
            rs = bs.query_required_reserve_ratio_data(start_date=start_date, end_date=end_date)
        elif data_type == 'money_supply_month':
            rs = bs.query_money_supply_data_month(start_date=start_date, end_date=end_date)
        elif data_type == 'money_supply_year':
            rs = bs.query_money_supply_data_year(start_date=start_date, end_date=end_date)
        else:
            raise ValueError(f"不支持的宏观数据类型: {data_type}")
        
        if rs.error_code != '0':
            raise RuntimeError(f"获取{data_type}数据失败: {rs.error_msg}")
        
        data_list = []
        max_rows = 10000  # 宏观数据可能比较多
        row_count = 0
        
        try:
            while rs.next() and row_count < max_rows:
                row_data = rs.get_row_data()
                data_list.append(row_data)
                row_count += 1
        except Exception as e:
            print(f"警告: 读取{data_type}数据时出错 (已读取{row_count}条): {e}")
            if not data_list:
                raise RuntimeError(f"读取{data_type}数据失败: {e}")
        
        return pd.DataFrame(data_list, columns=rs.fields)


def fetch_generic_data(
    query_type: str,
    **kwargs
) -> pd.DataFrame:
    """
    通用数据获取函数
    
    Args:
        query_type: 查询类型
        **kwargs: 查询参数
    
    Returns:
        DataFrame: 查询结果
    """
    with baostock_login_context():
        # 整个查询操作都在锁内执行，避免死锁
        with QUERY_LOCK:
            if query_type == 'k_data':
                rs = bs.query_history_k_data_plus(
                    code=kwargs.get('code'),
                    fields=kwargs.get('fields', 'date,open,high,low,close,volume'),
                    start_date=kwargs.get('start_date'),
                    end_date=kwargs.get('end_date'),
                    frequency=kwargs.get('frequency', 'd'),
                    adjustflag=kwargs.get('adjustflag', '3')
                )
            elif query_type == 'stock_basic':
                rs = bs.query_stock_basic(code=kwargs.get('code'))
            elif query_type == 'dividend':
                rs = bs.query_dividend_data(
                    code=kwargs.get('code'),
                    year=kwargs.get('year'),
                    yearType=kwargs.get('year_type', 'report')
                )
            elif query_type == 'adjust_factor':
                rs = bs.query_adjust_factor(
                    code=kwargs.get('code'),
                    start_date=kwargs.get('start_date'),
                    end_date=kwargs.get('end_date')
                )
            elif query_type == 'trade_dates':
                rs = bs.query_trade_dates(
                    start_date=kwargs.get('start_date'),
                    end_date=kwargs.get('end_date')
                )
            elif query_type == 'all_stock':
                rs = bs.query_all_stock(day=kwargs.get('date'))
            elif query_type == 'stock_industry':
                rs = bs.query_stock_industry(
                    code=kwargs.get('code'),
                    date=kwargs.get('date')
                )
            elif query_type == 'performance_express':
                rs = bs.query_performance_express_report(
                    code=kwargs.get('code'),
                    start_date=kwargs.get('start_date'),
                    end_date=kwargs.get('end_date')
                )
            elif query_type == 'forecast':
                rs = bs.query_forecast_report(
                    code=kwargs.get('code'),
                    start_date=kwargs.get('start_date'),
                    end_date=kwargs.get('end_date')
                )
            else:
                raise ValueError(f"不支持的查询类型: {query_type}")
            
            if rs.error_code != '0':
                raise RuntimeError(f"查询{query_type}失败: {rs.error_msg}")
            
            data_list = []
            max_rows = 10000  # 通用查询限制
            row_count = 0
            
            try:
                while rs.next() and row_count < max_rows:
                    row_data = rs.get_row_data()
                    data_list.append(row_data)
                    row_count += 1
            except Exception as e:
                print(f"警告: 读取{query_type}数据时出错 (已读取{row_count}条): {e}")
                if not data_list:
                    raise RuntimeError(f"读取{query_type}数据失败: {e}")
            
            return pd.DataFrame(data_list, columns=rs.fields)


def format_to_markdown(df: pd.DataFrame, title: str = "") -> str:
    """
    将DataFrame格式化为Markdown表格
    
    Args:
        df: 数据框
        title: 表格标题
    
    Returns:
        str: Markdown格式的表格
    """
    if df.empty:
        return f"### {title}\n\n暂无数据\n" if title else "暂无数据\n"
    
    result = f"### {title}\n\n" if title else ""
    result += df.to_markdown(index=False)
    return result
