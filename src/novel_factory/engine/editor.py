"""
编辑审校 — 规则检查 + 质量评估
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from novel_factory.llm.gateway import complete
from novel_factory.llm.skill_loader import SkillLoader

logger = logging.getLogger(__name__)

# 初始化 SkillLoader
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
skill_loader = SkillLoader(str(SKILLS_DIR))


async def review_chapter(
    project_id: str,
    chapter: dict,
    draft: str,
    characters: list[dict] | None = None,
    foreshadows: list[dict] | None = None,
    prev_summary: str = "",
    prev_issues: list[dict] | None = None,
) -> dict:
    """
    审校一章
    """
    logger.info("开始审校，章节: %s", chapter.get("title", "未知"))

    # 准备 SkillLoader 渲染上下文
    render_context = {
        "chapter": chapter,
        "draft": draft,
        "characters": characters or [],
        "foreshadows": foreshadows or [],
        "prev_summary": prev_summary or "无",
        "prev_issues": prev_issues or [],
    }

    system_prompt, user_prompt = skill_loader.render("editor", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="editor", temperature=0.1, max_tokens=4096)

    return _parse_review(response)

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
