"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置类"""
    
    # OpenAI配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai-proxy.org/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # 项目路径
    PROJECT_ROOT: Path = Path(__file__).parent
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output"))
    
    # 日志级别
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # 数据配置
    DEFAULT_K_LINE_YEARS: int = 3  # 默认获取3年K线数据
    NEWS_COUNT: int = 10  # 默认获取10条新闻
    
    @classmethod
    def validate(cls) -> bool:
        """验证必要配置"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY 未配置")
        return True
    
    @classmethod
    def ensure_output_dir(cls) -> Path:
        """确保输出目录存在"""
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        return cls.OUTPUT_DIR


config = Config()
