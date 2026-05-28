"""
记忆系统 — 管理前文摘要和上下文窗口
"""

from __future__ import annotations

import logging

from novel_factory.llm.gateway import complete

logger = logging.getLogger(__name__)


async def generate_summary(text: str, max_words: int = 100) -> str:
    """
    生成文本摘要

    Args:
        text: 原文
        max_words: 摘要最大字数

    Returns:
        摘要文本
    """
    messages = [
        {
            "role": "system",
            "content": f"你是一个文本摘要专家。请用不超过{max_words}字概括以下内容的关键信息，包括：人物、事件、情绪变化、关键对话要点。只输出摘要，不要任何说明。",
        },
        {"role": "user", "content": text},
    ]

    return await complete(messages=messages, role="summary", temperature=0.2, max_tokens=max_words * 2)


async def build_context(
    chapter: dict,
    scenes: list[dict] | None = None,
    prev_chapters_summary: str = "",
    characters: list[dict] | None = None,
) -> dict:
    """
    构建写作上下文窗口

    Args:
        chapter: 当前章节大纲
        scenes: 已生成的场景列表
        prev_chapters_summary: 前文摘要
        characters: 角色列表

    Returns:
        {"global_memory": str, "recent_summary": str, "sliding_window": str}
    """
    # 全局记忆：角色信息
    global_memory = ""
    if characters:
        global_memory = "\n".join(
            f"- {c.get('name', '')}: {c.get('personality', '')}, 当前状态: {c.get('current_state', '未知')}"
            for c in characters
        )

    # 近期摘要
    recent_summary = prev_chapters_summary or "（故事开始）"

    # 滑动窗口：最近场景原文
    sliding_window = ""
    if scenes:
        recent = scenes[-2:]  # 最近2个场景
        sliding_window = "\n---\n".join(
            s.get("draft", s.get("final_text", "")) for s in recent if s.get("draft") or s.get("final_text")
        )

    return {
        "global_memory": global_memory or "（暂无角色信息）",
        "recent_summary": recent_summary,
        "sliding_window": sliding_window or "（无前文）",
    }
