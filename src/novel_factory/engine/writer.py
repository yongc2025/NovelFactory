"""
正文作者 — 根据场景细纲生成正文
"""

from __future__ import annotations

import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import (
    CONTENT_RED_LINES,
    STYLE_INSTRUCTION,
    WRITER_SYSTEM,
    WRITER_USER,
    render_prompt,
)

logger = logging.getLogger(__name__)


async def write_scene(
    project_id: str,
    chapter: dict,
    scene: dict,
    characters: list[dict] | None = None,
    prev_summary: str = "",
) -> str:
    """
    为一个场景生成正文

    Args:
        project_id: 项目 ID
        chapter: 章节大纲
        scene: 场景细纲
        characters: 角色列表（用于保持一致性）
        prev_summary: 前文摘要

    Returns:
        正文文本（800-1500 字）
    """
    logger.info("开始生成正文，场景: %s", scene.get("location", "未知"))

    # 构建角色信息
    char_info = ""
    if characters:
        char_info = "\n".join(
            f"- {c.get('name', '未知')}: {c.get('personality', '')}, 说话风格: {c.get('speaking_style', c.get('voice_style', ''))}"
            for c in characters
        )

    # 构建场景大纲描述
    scene_outline = f"""
章节: {chapter.get('title', '')}
场景地点: {scene.get('location', '')}
氛围: {scene.get('atmosphere', '')}
出场角色: {', '.join(scene.get('characters_present', []))}
冲突: {scene.get('conflict', '')}
转折: {scene.get('turning_point', '')}
情绪: {scene.get('emotion_start', '')} → {scene.get('emotion_end', '')}
对话方向: {scene.get('dialogue_direction', '')}
感官细节: {scene.get('sensory_details', '')}
""".strip()

    system_prompt = render_prompt(
        WRITER_SYSTEM,
        style_instruction=STYLE_INSTRUCTION,
        content_red_lines=CONTENT_RED_LINES,
        global_memory=char_info or "（暂无角色信息）",
        recent_summary=prev_summary or "（故事开始）",
        sliding_window="（无前文）",
        current_task=f"撰写以下场景的正文",
    )

    user_prompt = render_prompt(
        WRITER_USER,
        scene_outline=scene_outline,
        character_info=char_info or "（暂无）",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    draft = await complete(messages=messages, role="writer", temperature=0.85, max_tokens=4096)

    logger.info("正文生成完成，约 %d 字", len(draft))
    return draft
