"""配置管理 -- 从环境变量 / .env 文件加载。"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，支持从环境变量和 .env 文件自动加载。"""

    # -- DeepSeek LLM --
    DEEPSEEK_API_KEY: str = Field(default="", description="DeepSeek API 密钥")
    DEEPSEEK_BASE_URL: str = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API 基础地址",
    )
    DEFAULT_MODEL: str = Field(default="deepseek-chat", description="默认模型 (V3)")
    REASONING_MODEL: str = Field(default="deepseek-reasoner", description="推理模型 (R1)")

    # -- 存储路径 --
    DB_PATH: str = Field(default="data/novel.db", description="SQLite 数据库路径")
    OUTPUT_DIR: str = Field(default="output/", description="输出目录")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @property
    def db_path_resolved(self) -> Path:
        """返回解析后的数据库文件绝对路径。"""
        return Path(self.DB_PATH).resolve()

    @property
    def output_dir_resolved(self) -> Path:
        """返回解析后的输出目录绝对路径。"""
        return Path(self.OUTPUT_DIR).resolve()


# 模块级单例
settings = Settings()
