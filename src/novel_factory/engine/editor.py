"""
编辑审校 — 规则检查 + 质量评估
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import (
    EDITOR_QUALITY_SYSTEM,
    EDITOR_QUALITY_USER,
    EDITOR_RULES_SYSTEM,
    EDITOR_RULES_USER,
    render_prompt,
)

logger = logging.getLogger(__name__)


async def review_chapter(
    project_id: str,
    chapter: dict,
    draft: str,
    characters: list[dict] | None = None,
    foreshadows: list[dict] | None = None,
) -> dict:
    """
    审校一章

    Args:
        project_id: 项目 ID
        chapter: 章节大纲
        draft: 正文初稿
        characters: 角色列表
        foreshadows: 伏笔列表

    Returns:
        审校报告 dict
    """
    logger.info("开始审校，章节: %s", chapter.get("title", "未知"))

    characters_info = "\n".join(
        f"- {c.get('name', '未知')}: {c.get('role', '')}, {c.get('personality', '')}"
        for c in (characters or [])
    )
    foreshadows_status = "\n".join(
        f"- [{f.get('status', '未知')}] {f.get('content', '')}"
        for f in (foreshadows or [])
    ) or "（暂无伏笔）"

    # 第一轮：规则检查
    rules_prompt = render_prompt(
        EDITOR_RULES_USER,
        chapter_title=chapter.get("title", ""),
        core_event=chapter.get("core_event", ""),
        characters_info=characters_info,
        foreshadows_status=foreshadows_status,
        chapter_draft=draft,
    )

    rules_messages = [
        {"role": "system", "content": EDITOR_RULES_SYSTEM},
        {"role": "user", "content": rules_prompt},
    ]

    rules_response = await complete(messages=rules_messages, role="editor_rules", temperature=0.1, max_tokens=2048)

    # 第二轮：质量评估
    quality_prompt = render_prompt(
        EDITOR_QUALITY_USER,
        chapter_title=chapter.get("title", ""),
        emotion_position=chapter.get("emotion_position", ""),
        emotion_arc=chapter.get("emotion_arc", ""),
        chapter_draft=draft,
        word_count=len(draft),
    )

    quality_messages = [
        {"role": "system", "content": EDITOR_QUALITY_SYSTEM},
        {"role": "user", "content": quality_prompt},
    ]

    quality_response = await complete(messages=quality_messages, role="editor_quality", temperature=0.3, max_tokens=2048)

    # 合并结果
    return _merge_review(rules_response, quality_response, len(draft))


def _merge_review(rules_response: str, quality_response: str, word_count: int) -> dict:
    """合并规则检查和质量评估结果"""
    review = {
        "total_words": word_count,
        "checks": {},
        "issues": [],
        "score": None,
    }

    # 解析规则检查
    try:
        json_str = rules_response
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        rules = json.loads(json_str.strip())
        review["checks"]["character_consistency"] = "通过" if rules.get("pass", False) else "发现问题"
        for issue in rules.get("issues", []):
            review["issues"].append(issue)
    except (json.JSONDecodeError, KeyError):
        review["checks"]["character_consistency"] = "待检查"

    # 解析质量评估
    try:
        json_str = quality_response
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        quality = json.loads(json_str.strip())
        review["score"] = quality.get("overall_score")
        review["quality"] = quality
    except (json.JSONDecodeError, KeyError):
        review["quality"] = {"note": "质量评估解析失败"}

    return review
