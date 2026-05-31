"""上下文存储 — 前文摘要 + 审校结果的文件读写

目录结构：
    data/<project_id>/context/
    ├── ch1_summary.md      # 第 1 章摘要
    ├── ch2_summary.md
    ├── ch1_review.json     # 第 1 章审校结果
    └── ...
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ContextStore:
    """上下文存储管理器"""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir

    def _context_dir(self, project_id: str) -> Path:
        """获取项目的 context 目录"""
        d = self.data_dir / project_id / "context"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def save_summary(self, project_id: str, ch_num: int, text: str) -> None:
        """保存章节摘要"""
        path = self._context_dir(project_id) / f"ch{ch_num}_summary.md"
        path.write_text(text, encoding="utf-8")
        logger.debug("摘要已保存: %s ch%d", project_id, ch_num)

    def get_summary(self, project_id: str, ch_num: int) -> str | None:
        """获取章节摘要"""
        path = self._context_dir(project_id) / f"ch{ch_num}_summary.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def get_recent_summaries(
        self, project_id: str, ch_num: int, window: int = 3,
    ) -> str:
        """获取最近 N 章的摘要拼接

        Args:
            project_id: 项目 ID
            ch_num: 当前章节号（从这章往前取）
            window: 往前取几章

        Returns:
            拼接后的摘要文本
        """
        summaries = []
        for i in range(max(1, ch_num - window), ch_num):
            s = self.get_summary(project_id, i)
            if s:
                summaries.append(f"第{i}章摘要：{s}")
        return "\n".join(summaries) if summaries else ""

    def save_chapter_review(
        self, project_id: str, ch_num: int, review: dict,
    ) -> None:
        """保存章节审校结果"""
        path = self._context_dir(project_id) / f"ch{ch_num}_review.json"
        path.write_text(
            json.dumps(review, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.debug("审校结果已保存: %s ch%d", project_id, ch_num)

    def get_chapter_review(
        self, project_id: str, ch_num: int,
    ) -> dict | None:
        """获取章节审校结果"""
        path = self._context_dir(project_id) / f"ch{ch_num}_review.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return None
        return None

    def get_recent_reviews(
        self, project_id: str, ch_num: int, window: int = 3,
    ) -> list[dict]:
        """获取最近 N 章的审校结果"""
        reviews = []
        for i in range(max(1, ch_num - window), ch_num):
            r = self.get_chapter_review(project_id, i)
            if r:
                reviews.append({"chapter": i, **r})
        return reviews
