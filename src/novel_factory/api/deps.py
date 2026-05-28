"""FastAPI 依赖注入

提供 ProjectStore 和 NovelPipeline 的单例获取。
"""

from __future__ import annotations

from functools import lru_cache

from novel_factory.db.project_store import ProjectStore
from novel_factory.pipeline import NovelPipeline


@lru_cache()
def get_store() -> ProjectStore:
    """获取 ProjectStore 单例"""
    return ProjectStore()


@lru_cache()
def get_pipeline() -> NovelPipeline:
    """获取 NovelPipeline 单例"""
    return NovelPipeline()
