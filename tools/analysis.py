"""
分析工具模块
提供综合分析功能
"""
from typing import Literal
from langchain_core.tools import tool


@tool
def get_stock_analysis(
    code: str,
    analysis_type: Literal['fundamental', 'technical', 'comprehensive'] = 'comprehensive'
) -> str:
    """
    生成股票分析报告
    
    此工具提供基于数据的分析框架，而非投资建议。
    
    Args:
        code: 股票代码，如 sh.600519
        analysis_type: 分析类型
            - fundamental: 基本面分析
            - technical: 技术分析
            - comprehensive: 综合分析
    
    Returns:
        str: 分析框架和建议的Markdown格式文本
    """
    analysis_templates = {
        'fundamental': """### 基本面分析框架

#### 建议获取的数据
1. **盈利能力** (get_profit_data)
   - ROE (净资产收益率): 衡量股东回报
   - 净利润率: 衡量盈利效率
   
2. **成长能力** (get_growth_data)
   - 营收增长率: 评估业务扩张
   - 净利润增长率: 评估盈利增长
   
3. **运营能力** (get_operation_data)
   - 存货周转率: 评估运营效率
   - 应收账款周转率: 评估资金回收

4. **偿债能力** (get_balance_data)
   - 资产负债率: 评估财务风险
   - 流动比率: 评估短期偿债能力

5. **现金流** (get_cash_flow_data)
   - 经营活动现金流: 评估造血能力

#### 分析要点
- 各项指标的趋势变化
- 与行业平均水平的对比
- 财务数据的一致性和可靠性
""",
        'technical': """### 技术分析框架

#### 建议获取的数据
1. **K线数据** (get_historical_k_data)
   - 日K线: 短期趋势
   - 周K线: 中期趋势
   - 月K线: 长期趋势

2. **价格分析**
   - 支撑位和阻力位
   - 均线系统 (MA5, MA10, MA20, MA60)
   - 价格形态

3. **成交量分析**
   - 量价配合
   - 成交量变化趋势

#### 分析要点
- 趋势方向判断
- 买卖信号识别
- 风险收益比评估
""",
        'comprehensive': """### 综合分析框架

#### 第一步: 公司概况
- 使用 get_stock_basic_info 获取基本信息
- 使用 get_stock_industry 确定行业分类

#### 第二步: 基本面分析
- 使用财务数据工具获取最近4个季度数据
- 分析盈利、成长、运营、偿债能力

#### 第三步: 技术分析
- 使用 get_historical_k_data 获取3年K线数据
- 分析价格趋势和成交量

#### 第四步: 估值分析
- 获取行业对标公司数据
- 使用 get_dividend_data 分析分红情况

#### 第五步: 新闻分析
- 使用 crawl_news 获取最新新闻
- 评估市场情绪和风险

#### 综合评估要点
- 多维度交叉验证
- 风险因素识别
- 投资价值判断
"""
    }
    
    return analysis_templates.get(analysis_type, analysis_templates['comprehensive'])
