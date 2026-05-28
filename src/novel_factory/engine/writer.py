"""
正文作者 — 场景级正文生成

职责：
1. 构建完整的上下文（通过记忆系统）
2. 调用 LLM 生成 800-1500 字的场景正文
3. 确保角色一致性、情绪连贯性、伏笔呼应
4. 将正文存入数据库
"""

from __future__ import annotations

import json
import logging

from novel_factory.db.connection import get_connection
from novel_factory.engine.memory import MemoryManager
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import (
    CONTENT_RED_LINES,
    STYLE_INSTRUCTION,
    WRITER_SYSTEM,
    WRITER_USER,
    render_prompt,
)

logger = logging.getLogger(__name__)


async def write_scene(project_id: str, scene_id: str) -> str:
    """
    撰写场景正文

    使用记忆系统构建上下文，调用 LLM 生成 800-1500 字的场景正文。

    Args:
        project_id: 项目 ID
        scene_id: 场景 ID

    Returns:
        生成的正文文本（800-1500 字）
    """
    logger.info("开始撰写正文，场景: %s", scene_id)

    with get_connection() as conn:
        scene = conn.execute(
            "SELECT s.*, c.chapter_num, c.title as chapter_title, "
            "c.core_event, c.emotion_position, c.emotion_arc "
            "FROM scenes s "
            "JOIN chapters c ON s.chapter_id = c.id "
            "WHERE s.id = ? AND s.project_id = ?",
            (scene_id, project_id),
        ).fetchone()

        if not scene:
            raise ValueError(f"场景不存在: {scene_id}")

        # 获取出场角色信息
        characters_info = ""
        if scene["characters_present"]:
            try:
                char_names = json.loads(scene["characters_present"])
                if isinstance(char_names, list) and char_names:
                    placeholders = ",".join("?" * len(char_names))
                    chars = conn.execute(
                        f"SELECT name, role, personality_surface, voice_style, "
                        f"core_desire, current_state "
                        f"FROM characters WHERE project_id = ? AND name IN ({placeholders})",
                        (project_id, *char_names),
                    ).fetchall()
                    char_texts = []
                    for c in chars:
                        char_texts.append(
                            f"- {c['name']}（{c['role'] or '未设定'}）: "
                            f"{c['personality_surface'] or '未设定'}\n"
                            f"  说话风格: {c['voice_style'] or '未设定'}\n"
                            f"  当前状态: {c['current_state'] or '未设定'}"
                        )
                    characters_info = "\n".join(char_texts)
            except (json.JSONDecodeError, TypeError):
                characters_info = scene["characters_present"]

    # 使用记忆系统构建上下文
    memory = MemoryManager()
    context = await memory.build_context_window(
        project_id=project_id,
        current_chapter=scene["chapter_num"],
        current_scene=scene["scene_num"],
    )

    # 构建场景大纲
    scene_outline_parts = [
        f"地点: {scene['location'] or '未设定'}",
        f"氛围: {scene['atmosphere'] or '未设定'}",
        f"出场角色: {scene['characters_present'] or '未设定'}",
        f"角色目标: {scene['character_goals'] or '未设定'}",
        f"核心冲突: {scene['conflict'] or '未设定'}",
        f"转折点: {scene['turning_point'] or '未设定'}",
        f"情绪变化: {scene['emotion_start'] or '?'} → {scene['emotion_end'] or '?'}",
        f"对话方向: {scene['dialogue_direction'] or '未设定'}",
        f"感官细节: {scene['sensory_details'] or '未设定'}",
    ]
    scene_outline = "\n".join(scene_outline_parts)

    system_prompt = render_prompt(
        WRITER_SYSTEM,
        style_instruction=STYLE_INSTRUCTION,
        content_red_lines=CONTENT_RED_LINES,
        global_memory=context["global_memory"],
        recent_summary=context["recent_summary"],
        sliding_window=context["sliding_window"],
        current_task=context["current_task"],
    )

    user_prompt = render_prompt(
        WRITER_USER,
        scene_outline=scene_outline,
        character_info=characters_info or "暂无详细角色信息",
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    draft = await complete(messages=messages, temperature=0.85, max_tokens=4096)

    # 清理输出
    draft = draft.strip()
    if draft.startswith("```"):
        lines = draft.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        draft = "\n".join(lines)

    # 验证字数
    word_count = len(draft)
    if word_count < 600:
        logger.warning("正文过短: %d 字，目标 800-1500 字", word_count)
    elif word_count > 2000:
        logger.warning("正文过长: %d 字，目标 800-1500 字", word_count)

    # 生成场景摘要
    summary = await memory.generate_scene_summary(draft)

    # 存入数据库
    with get_connection() as conn:
        conn.execute(
            "UPDATE scenes SET final_text = ?, summary = ?, word_count = ? WHERE id = ?",
            (draft, summary, word_count, scene_id),
        )

    logger.info("正文撰写完成，场景: %s，字数: %d", scene_id, word_count)
    return draft
