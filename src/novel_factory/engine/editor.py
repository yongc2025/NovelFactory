"""
编辑审校 — 规则检查 + 质量评估

职责：
1. 第一轮：规则检查（角色名一致性、字数、红线、情节逻辑、时间线、伏笔追踪）
2. 第二轮：质量评估（节奏、情绪、对话、去AI味、可读性、金句密度）
3. 输出结构化的审校报告
"""

from __future__ import annotations

import json
import logging

from novel_factory.db.connection import get_connection
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import (
    EDITOR_QUALITY_SYSTEM,
    EDITOR_QUALITY_USER,
    EDITOR_RULES_SYSTEM,
    EDITOR_RULES_USER,
    render_prompt,
)

logger = logging.getLogger(__name__)


async def review_chapter(project_id: str, chapter_id: str) -> dict:
    """
    审校章节

    对章节进行两轮审校：
    1. 规则检查：确保没有硬性错误
    2. 质量评估：评估文学质量和可读性

    Args:
        project_id: 项目 ID
        chapter_id: 章节 ID

    Returns:
        审校报告，包含 rules_check, quality_review, overall_pass, summary
    """
    logger.info("开始审校章节: %s", chapter_id)

    with get_connection() as conn:
        chapter = conn.execute(
            "SELECT * FROM chapters WHERE id = ? AND project_id = ?",
            (chapter_id, project_id),
        ).fetchone()

        if not chapter:
            raise ValueError(f"章节不存在: {chapter_id}")

        scenes = conn.execute(
            "SELECT scene_num, final_text, location, characters_present "
            "FROM scenes WHERE chapter_id = ? ORDER BY scene_num",
            (chapter_id,),
        ).fetchall()

        characters = conn.execute(
            "SELECT name, role, personality_surface, voice_style, current_state "
            "FROM characters WHERE project_id = ?",
            (project_id,),
        ).fetchall()

        foreshadows = conn.execute(
            "SELECT content, status, planted_chapter, target_chapter "
            "FROM foreshadows WHERE project_id = ?",
            (project_id,),
        ).fetchall()

    # 合并正文
    chapter_draft_parts = []
    total_word_count = 0
    for s in scenes:
        if s["final_text"]:
            chapter_draft_parts.append(
                f"--- 场景{s['scene_num']}（{s['location'] or '未知地点'}）---\n"
                f"{s['final_text']}"
            )
            total_word_count += len(s["final_text"])

    chapter_draft = "\n\n".join(chapter_draft_parts)
    if not chapter_draft:
        return {
            "rules_check": {
                "pass": False,
                "issues": [{"type": "空章节", "severity": "error", "detail": "章节没有正文"}],
            },
            "quality_review": None,
            "overall_pass": False,
            "summary": "章节没有正文，无法审校",
        }

    # 角色信息
    char_texts = []
    for c in characters:
        char_texts.append(
            f"- {c['name']}（{c['role'] or '未设定'}）: "
            f"{c['personality_surface'] or '未设定'}\n"
            f"  说话风格: {c['voice_style'] or '未设定'}\n"
            f"  当前状态: {c['current_state'] or '未设定'}"
        )
    characters_info = "\n".join(char_texts) if char_texts else "暂无角色信息"

    # 伏笔状态
    fs_texts = []
    for fs in foreshadows:
        fs_texts.append(
            f"- {fs['content']}（状态: {fs['status']}）\n"
            f"  埋设: 第{fs['planted_chapter'] or '?'}章 → "
            f"回收: 第{fs['target_chapter'] or '?'}章"
        )
    foreshadows_status = "\n".join(fs_texts) if fs_texts else "暂无伏笔"

    # 第一轮：规则检查
    logger.info("第一轮：规则检查")
    rules_result = await _check_rules(chapter, characters_info, foreshadows_status, chapter_draft)

    # 第二轮：质量评估
    logger.info("第二轮：质量评估")
    quality_result = await _check_quality(chapter, chapter_draft, total_word_count)

    # 汇总
    overall_pass = rules_result.get("pass", False)
    if quality_result and quality_result.get("overall_score", 0) < 5:
        overall_pass = False

    summary_parts = []
    if rules_result.get("pass"):
        summary_parts.append("? 规则检查通过")
    else:
        errors = [i for i in rules_result.get("issues", []) if i.get("severity") == "error"]
        summary_parts.append(f"? 规则检查未通过，{len(errors)} 个错误")

    if quality_result:
        score = quality_result.get("overall_score", 0)
        summary_parts.append(f"?? 质量评分: {score}/10")
        if quality_result.get("highlights"):
            summary_parts.append(f"? 亮点: {', '.join(quality_result['highlights'][:2])}")
        if quality_result.get("improvements"):
            summary_parts.append(f"?? 建议: {', '.join(quality_result['improvements'][:2])}")

    report = {
        "rules_check": rules_result,
        "quality_review": quality_result,
        "overall_pass": overall_pass,
        "word_count": total_word_count,
        "summary": "\n".join(summary_parts),
    }

    logger.info("审校完成，结果: %s", "通过" if overall_pass else "未通过")
    return report


async def _check_rules(chapter, characters_info, foreshadows_status, chapter_draft) -> dict:
    """第一轮：规则检查"""
    user_prompt = render_prompt(
        EDITOR_RULES_USER,
        chapter_title=chapter["title"] or "未命名",
        core_event=chapter["core_event"] or "未设定",
        characters_info=characters_info,
        foreshadows_status=foreshadows_status,
        chapter_draft=chapter_draft,
    )

    messages = [
        {"role": "system", "content": EDITOR_RULES_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, temperature=0.1, max_tokens=2048)
    return _parse_json_response(response, "规则检查")


async def _check_quality(chapter, chapter_draft, word_count) -> dict | None:
    """第二轮：质量评估"""
    user_prompt = render_prompt(
        EDITOR_QUALITY_USER,
        chapter_title=chapter["title"] or "未命名",
        emotion_position=chapter["emotion_position"] or "未设定",
        emotion_arc=chapter["emotion_arc"] or "未设定",
        chapter_draft=chapter_draft,
        word_count=word_count,
    )

    messages = [
        {"role": "system", "content": EDITOR_QUALITY_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, temperature=0.3, max_tokens=2048)
    return _parse_json_response(response, "质量评估")


def _parse_json_response(response: str, context: str) -> dict:
    """解析 LLM 返回的 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        return json.loads(json_str.strip())
    except (json.JSONDecodeError, IndexError) as e:
        logger.error("%s JSON 解析失败: %s", context, e)
        return {
            "pass": False,
            "issues": [{"type": "解析错误", "severity": "error", "detail": str(e)}],
            "summary": f"{context}结果解析失败",
        }
