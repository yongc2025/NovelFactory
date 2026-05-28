"""配置管理 -- 从环境变量 / .env 文件加载。

支持多模型配置：
  - deepseek-v4-pro  (火山引擎 Ark，推理/复杂任务)
  - deepseek-v4-flash (火山引擎 Ark，快速/低成本)
  - mimo-v2.5-pro     (小米 MiMo，备选)
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，支持从环境变量和 .env 文件自动加载。"""

    # -- 模型 1: DeepSeek V4 Pro (推理/复杂任务) --
    PRO_MODEL_NAME: str = Field(default="deepseek-v4-pro", description="Pro 模型名称")
    PRO_MODEL_BASE_URL: str = Field(
        default="https://ark.cn-beijing.volces.com/api/coding/v3",
        description="Pro 模型 API 地址",
    )
    PRO_MODEL_API_KEY: str = Field(default="", description="Pro 模型 API 密钥")

    # -- 模型 2: DeepSeek V4 Flash (快速/低成本) --
    FLASH_MODEL_NAME: str = Field(default="deepseek-v4-flash", description="Flash 模型名称")
    FLASH_MODEL_BASE_URL: str = Field(
        default="https://ark.cn-beijing.volces.com/api/coding/v3",
        description="Flash 模型 API 地址",
    )
    FLASH_MODEL_API_KEY: str = Field(default="", description="Flash 模型 API 密钥")

    # -- 模型 3: MiMo V2.5 Pro (备选) --
    MIMO_MODEL_NAME: str = Field(default="mimo-v2.5-pro", description="MiMo 模型名称")
    MIMO_MODEL_BASE_URL: str = Field(
        default="https://token-plan-cn.xiaomimimo.com/v1",
        description="MiMo 模型 API 地址",
    )
    MIMO_MODEL_API_KEY: str = Field(default="", description="MiMo 模型 API 密钥")

    # -- 默认模型选择 --
    # pro / flash / mimo
    DEFAULT_PROVIDER: str = Field(default="flash", description="默认模型提供者")

    # -- 存储路径 --
    DB_PATH: str = Field(default="data/novel.db", description="SQLite 数据库路径")
    OUTPUT_DIR: str = Field(default="output/", description="输出目录")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_model_config(self, provider: str | None = None) -> dict:
        """获取指定模型的配置。

        Args:
            provider: 模型提供者 (pro/flash/mimo)，默认使用 DEFAULT_PROVIDER

        Returns:
            dict: {"name": str, "base_url": str, "api_key": str}
        """
        provider = (provider or self.DEFAULT_PROVIDER).lower()

        if provider == "pro":
            return {
                "name": self.PRO_MODEL_NAME,
                "base_url": self.PRO_MODEL_BASE_URL,
                "api_key": self.PRO_MODEL_API_KEY,
            }
        elif provider == "flash":
            return {
                "name": self.FLASH_MODEL_NAME,
                "base_url": self.FLASH_MODEL_BASE_URL,
                "api_key": self.FLASH_MODEL_API_KEY,
            }
        elif provider == "mimo":
            return {
                "name": self.MIMO_MODEL_NAME,
                "base_url": self.MIMO_MODEL_BASE_URL,
                "api_key": self.MIMO_MODEL_API_KEY,
            }
        else:
            raise ValueError(f"未知的模型提供者: {provider}，可选: pro/flash/mimo")

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
