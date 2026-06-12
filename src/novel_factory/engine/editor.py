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

    # 解析并返回结果
    return _parse_review_json(response, len(draft))


def _parse_review_json(response: str, word_count: int) -> dict:
    """解析 LLM 返回的审校 JSON"""
    review = {
        "total_words": word_count,
        "checks": {},
        "issues": [],
        "score": None,
        "quality": {},
    }

    try:
        json_str = response
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        data = json.loads(json_str.strip())

        # 1. 解析规则检查 (rules_check)
        rc = data.get("rules_check", {})
        review["checks"]["pass"] = rc.get("pass", False)
        review["issues"] = rc.get("issues", [])

        # 2. 解析质量评估 (quality_review)
        qr = data.get("quality_review", {})
        review["score"] = qr.get("overall_score")
        review["quality"] = qr
        
        # 兼容性处理：如果 issues 在根级或质量评估级
        if not review["issues"] and data.get("issues"):
            review["issues"] = data.get("issues")
        elif not review["issues"] and qr.get("issues"):
            review["issues"] = qr.get("issues")

    except Exception as e:
        logger.error("审校 JSON 解析失败: %s", e)
        review["error"] = "解析失败"
        review["raw_response"] = response[:500]

    return review
