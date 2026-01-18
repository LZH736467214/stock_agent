"""
Prompt模块初始化
"""
from .planner import PLANNER_PROMPT
from .fundamental import FUNDAMENTAL_PROMPT
from .technical import TECHNICAL_PROMPT
from .valuation import VALUATION_PROMPT
from .news import NEWS_PROMPT
from .summarizer import SUMMARIZER_PROMPT

__all__ = [
    'PLANNER_PROMPT',
    'FUNDAMENTAL_PROMPT',
    'TECHNICAL_PROMPT',
    'VALUATION_PROMPT',
    'NEWS_PROMPT',
    'SUMMARIZER_PROMPT',
]
