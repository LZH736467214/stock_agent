"""
新闻爬取工具模块
提供新闻爬取和情感/风险分析功能
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import quote
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
import sys
sys.path.insert(0, str(__file__).rsplit('\\', 2)[0])
from config import config


def _search_baidu_news(query: str, num_results: int = 10) -> List[Dict]:
    """
    使用百度搜索爬取新闻
    
    Args:
        query: 搜索关键词
        num_results: 返回结果数量
    
    Returns:
        新闻列表
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # 百度新闻搜索URL
    url = f"https://www.baidu.com/s?wd={quote(query + ' 新闻')}&tn=news"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        
        news_list = []
        # 解析搜索结果
        results = soup.select('.result-op, .result')[:num_results]
        
        for item in results:
            title_elem = item.select_one('h3 a, .news-title a')
            content_elem = item.select_one('.c-abstract, .news-content')
            source_elem = item.select_one('.c-author, .news-source')
            
            if title_elem:
                news = {
                    'title': title_elem.get_text(strip=True),
                    'url': title_elem.get('href', ''),
                    'content': content_elem.get_text(strip=True) if content_elem else '',
                    'source': source_elem.get_text(strip=True) if source_elem else ''
                }
                news_list.append(news)
        
        return news_list
    except Exception as e:
        return [{'title': f'新闻获取失败: {str(e)}', 'content': '', 'url': '', 'source': ''}]


def _analyze_news_sentiment_risk(news_list: List[Dict], company_name: str) -> Dict:
    """
    使用LLM分析新闻的情感和风险
    
    Args:
        news_list: 新闻列表
        company_name: 公司名称
    
    Returns:
        包含情感和风险分析的字典
    """
    if not news_list:
        return {
            'sentiment_score': 3,
            'risk_score': 3,
            'analysis': '未获取到相关新闻',
            'news_summary': []
        }
    
    # 构建新闻摘要
    news_text = "\n".join([
        f"标题: {n['title']}\n内容: {n['content'][:200]}"
        for n in news_list[:5]  # 只分析前5条
    ])
    
    prompt = f"""请分析以下关于"{company_name}"的新闻，并给出情感评分和风险评分。

新闻内容:
{news_text}

请按以下格式回复:
情感评分: [1-5的整数，1=极负面，2=负面，3=中性，4=正面，5=极正面]
风险评分: [1-5的整数，1=极低风险，2=低风险，3=中等风险，4=高风险，5=极高风险]
情感分析: [简要分析市场情绪]
风险分析: [简要分析潜在风险]
新闻要点: [列出3-5个关键信息点]
"""
    
    try:
        llm = ChatOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            model=config.OPENAI_MODEL,
            temperature=0
        )
        response = llm.invoke(prompt)
        analysis_text = response.content
        
        # 解析评分
        sentiment_score = 3
        risk_score = 3
        
        for line in analysis_text.split('\n'):
            if '情感评分' in line:
                try:
                    sentiment_score = int(''.join(filter(str.isdigit, line.split(':')[-1][:5])))
                except:
                    pass
            elif '风险评分' in line:
                try:
                    risk_score = int(''.join(filter(str.isdigit, line.split(':')[-1][:5])))
                except:
                    pass
        
        return {
            'sentiment_score': max(1, min(5, sentiment_score)),
            'risk_score': max(1, min(5, risk_score)),
            'analysis': analysis_text,
            'news_summary': [{'title': n['title'], 'source': n['source']} for n in news_list[:5]]
        }
    except Exception as e:
        return {
            'sentiment_score': 3,
            'risk_score': 3,
            'analysis': f'分析失败: {str(e)}',
            'news_summary': [{'title': n['title'], 'source': n['source']} for n in news_list[:5]]
        }


@tool
def crawl_news(query: str, num_results: int = 10) -> str:
    """
    爬取与查询词相关的新闻并进行情感/风险分析
    
    情感评分说明:
    - 1: 极负面 - 市场极度恐慌
    - 2: 负面 - 市场情绪悲观
    - 3: 中性 - 市场情绪平稳
    - 4: 正面 - 市场情绪积极
    - 5: 极正面 - 市场极度乐观
    
    风险评分说明:
    - 1: 极低风险 - 基本面稳固
    - 2: 低风险 - 风险可控
    - 3: 中等风险 - 需要关注
    - 4: 高风险 - 存在隐患
    - 5: 极高风险 - 重大风险
    
    Args:
        query: 搜索关键词 (如公司名称)
        num_results: 返回新闻数量，默认10条
    
    Returns:
        str: 包含新闻列表和分析结果的Markdown格式文本
    """
    # 爬取新闻
    news_list = _search_baidu_news(query, num_results)
    
    # 分析情感和风险
    analysis = _analyze_news_sentiment_risk(news_list, query)
    
    # 格式化输出
    result = f"""### {query} 相关新闻分析

#### 评分概览
| 指标 | 评分 | 说明 |
|------|------|------|
| 情感评分 | {analysis['sentiment_score']}/5 | {'极负面' if analysis['sentiment_score']==1 else '负面' if analysis['sentiment_score']==2 else '中性' if analysis['sentiment_score']==3 else '正面' if analysis['sentiment_score']==4 else '极正面'} |
| 风险评分 | {analysis['risk_score']}/5 | {'极低风险' if analysis['risk_score']==1 else '低风险' if analysis['risk_score']==2 else '中等风险' if analysis['risk_score']==3 else '高风险' if analysis['risk_score']==4 else '极高风险'} |

#### 详细分析
{analysis['analysis']}

#### 新闻列表
"""
    
    for i, news in enumerate(news_list[:5], 1):
        result += f"\n{i}. **{news['title']}**\n   - 来源: {news['source']}\n   - 摘要: {news['content'][:100]}...\n"
    
    return result
