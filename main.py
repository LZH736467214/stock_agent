"""
多Agent股票顾问系统 - 主入口
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from config import config
from graph.workflow import create_stock_analysis_graph_v2

# 创建CLI应用
app = typer.Typer(
    name="stock-advisor",
    help="多Agent股票顾问系统 - 基于LangGraph的智能股票分析"
)

console = Console()


def save_report(report: str, company_name: str, stock_code: str) -> Path:
    """
    保存报告到文件
    
    Args:
        report: 报告内容
        company_name: 公司名称
        stock_code: 股票代码
    
    Returns:
        报告文件路径
    """
    config.ensure_output_dir()
    
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_name = company_name.replace(' ', '_').replace('/', '_')
    safe_code = stock_code.replace('.', '_')
    filename = f"{safe_name}_{safe_code}_{timestamp}.md"
    
    filepath = config.OUTPUT_DIR / filename
    filepath.write_text(report, encoding='utf-8')
    
    return filepath


@app.command()
def analyze(
    query: str = typer.Argument(..., help="分析查询，如：'分析贵州茅台的投资价值'"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="指定输出文件路径"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="显示详细输出")
):
    """
    分析股票投资价值
    
    示例:
        python main.py analyze "分析贵州茅台的投资价值"
        python main.py analyze "五粮液怎么样" -o report.md
    """
    console.print(Panel.fit(
        "[bold blue]多Agent股票顾问系统[/bold blue]\n"
        "[dim]Powered by LangGraph & OpenAI[/dim]",
        border_style="blue"
    ))
    
    # 验证配置
    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]配置错误: {e}[/red]")
        console.print("[yellow]请复制 .env.example 为 .env 并配置 OPENAI_API_KEY[/yellow]")
        raise typer.Exit(1)
    
    console.print(f"\n[cyan]分析查询:[/cyan] {query}\n")
    
    # 创建工作流
    graph = create_stock_analysis_graph_v2()
    
    # 初始状态
    initial_state = {
        'user_query': query,
        'company_name': '',
        'stock_code': '',
        'market': '',
        'fundamental_analysis': None,
        'technical_analysis': None,
        'valuation_analysis': None,
        'news_analysis': None,
        'final_report': None,
        'error': None,
        'messages': []
    }
    
    # 执行工作流
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]正在分析...", total=None)
        
        try:
            # 执行图
            result = graph.invoke(initial_state)
            
            progress.update(task, description="[green]分析完成!")
            
        except Exception as e:
            progress.update(task, description=f"[red]分析失败: {e}")
            if verbose:
                console.print_exception()
            raise typer.Exit(1)
    
    # 处理结果
    if result.get('error'):
        console.print(f"\n[red]错误: {result['error']}[/red]")
        raise typer.Exit(1)
    
    if not result.get('final_report'):
        console.print("\n[yellow]警告: 未能生成完整报告[/yellow]")
        if result.get('stock_code'):
            console.print(f"股票代码: {result['stock_code']}")
        raise typer.Exit(1)
    
    # 显示报告
    report = result['final_report']
    
    if verbose:
        console.print("\n" + "="*50)
        console.print(Markdown(report))
        console.print("="*50 + "\n")
    
    # 保存报告
    if output:
        filepath = Path(output)
    else:
        filepath = save_report(
            report,
            result.get('company_name', 'unknown'),
            result.get('stock_code', 'unknown')
        )
    
    filepath.write_text(report, encoding='utf-8')
    console.print(f"\n[green]报告已保存至:[/green] {filepath}")
    
    # 显示摘要
    console.print(Panel(
        f"[bold]{result.get('company_name', '未知')}[/bold] ({result.get('stock_code', '未知')})\n"
        f"市场: {result.get('market', '未知')}",
        title="分析结果",
        border_style="green"
    ))


@app.command()
def interactive():
    """
    进入交互模式，可以连续分析多只股票
    """
    console.print(Panel.fit(
        "[bold blue]多Agent股票顾问系统 - 交互模式[/bold blue]\n"
        "[dim]输入 'quit' 或 'exit' 退出[/dim]",
        border_style="blue"
    ))
    
    # 验证配置
    try:
        config.validate()
    except ValueError as e:
        console.print(f"[red]配置错误: {e}[/red]")
        raise typer.Exit(1)
    
    # 创建工作流
    graph = create_stock_analysis_graph_v2()
    
    while True:
        try:
            query = console.input("\n[cyan]请输入分析查询 > [/cyan]")
            
            if query.lower() in ['quit', 'exit', 'q']:
                console.print("[yellow]再见![/yellow]")
                break
            
            if not query.strip():
                continue
            
            # 执行分析
            console.print("\n[dim]正在分析...[/dim]")
            
            initial_state = {
                'user_query': query,
                'company_name': '',
                'stock_code': '',
                'market': '',
                'fundamental_analysis': None,
                'technical_analysis': None,
                'valuation_analysis': None,
                'news_analysis': None,
                'final_report': None,
                'error': None,
                'messages': []
            }
            
            result = graph.invoke(initial_state)
            
            if result.get('final_report'):
                # 保存并显示
                filepath = save_report(
                    result['final_report'],
                    result.get('company_name', 'unknown'),
                    result.get('stock_code', 'unknown')
                )
                console.print(f"\n[green]报告已保存:[/green] {filepath}")
                
                # 显示摘要
                console.print(Markdown(result['final_report'][:500] + "...\n\n*[报告已截断，完整内容请查看文件]*"))
            else:
                console.print("[red]分析失败[/red]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]已中断[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]错误: {e}[/red]")


@app.command()
def version():
    """显示版本信息"""
    console.print("[bold]多Agent股票顾问系统[/bold]")
    console.print("版本: 1.0.0")
    console.print("基于: LangGraph + OpenAI")


if __name__ == "__main__":
    app()
