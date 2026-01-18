"""
新闻爬取功能测试脚本 - 验证修复后的多源新闻获取
"""
import sys
sys.path.insert(0, 'c:\\gitclones\\stock_agent')

from tools.news_crawler import _search_sina_news, _search_baidu_news, _search_news, crawl_news

def test_news_sources():
    """测试各数据源"""
    query = '同花顺'
    
    print('=== 测试新浪财经新闻 ===')
    sina_news = _search_sina_news(query, 5)
    print(f'获取到 {len(sina_news)} 条新闻')
    for i, news in enumerate(sina_news[:3], 1):
        print(f'{i}. {news["title"][:50]}...')
    
    print('\n=== 测试多源新闻搜索 ===')
    news_list = _search_news(query, 5)
    print(f'获取到 {len(news_list)} 条新闻')
    for i, news in enumerate(news_list[:3], 1):
        print(f'{i}. {news["title"][:50]}...')
    
    print('\n=== 测试 crawl_news 工具函数 ===')
    result = crawl_news.invoke({'query': query, 'num_results': 5})
    print(result[:1000])  # 只打印前1000字符
    
    # 检验结果
    if len(sina_news) >= 3:
        print('\n\n✅ 测试通过: 新闻爬取功能正常工作!')
    else:
        print('\n\n❌ 测试失败: 新闻数量不足')

if __name__ == '__main__':
    test_news_sources()
