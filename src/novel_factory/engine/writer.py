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
    params: dict | None = None,
) -> str:
    """
    为一个场景生成正文

    Args:
        project_id: 项目 ID
        chapter: 章节大纲
        scene: 场景细纲
        characters: 角色列表
        prev_summary: 前文摘要
        params: 项目创建参数，包含 tone/style_sample/chapter_word_range 等
    """
    params = params or {}
    logger.info("开始生成正文，场景: %s", scene.get("location", "未知"))

    # 角色信息
    char_info = ""
    if characters:
        char_info = "\n".join(
            f"- {c.get('name', '未知')}: {c.get('personality', '')}, 说话风格: {c.get('speaking_style', c.get('voice_style', ''))}"
            for c in characters
        )

    # 场景大纲
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

    # 额外风格指令
    extra_style = ""
    if params.get("tone"):
        tone_map = {
            "爽文": "节奏要快，爽点密集，打脸要狠，读者看了要喊爽",
            "虐文": "情感要细腻，虐心要到位，但虐中要有甜，不能纯虐",
            "甜文": "甜度要高，细节要暖，让人看了嘴角上扬",
            "悬疑": "悬念要层层递进，每段都要有信息量，让人猜不到下一步",
            "热血": "节奏紧凑，战斗场面要有画面感，燃点要到位",
        }
        extra_style += f"\n基调要求：{tone_map.get(params['tone'], params['tone'])}"
    if params.get("style_sample"):
        extra_style += f"\n参考风格样本（模仿这种写作风格）：\n{params['style_sample'][:500]}"
    if params.get("chapter_word_range"):
        lo, hi = params["chapter_word_range"]
        extra_style += f"\n本章目标字数：{lo}-{hi}字"
    if params.get("target_audience") and params["target_audience"] != "general":
        audience = "女频读者（注重情感细腻度、角色心理描写）" if params["target_audience"] == "female" else "男频读者（注重爽感、节奏、实力展现）"
        extra_style += f"\n目标读者：{audience}"

    system_prompt = render_prompt(
        WRITER_SYSTEM,
        style_instruction=STYLE_INSTRUCTION + extra_style,
        content_red_lines=CONTENT_RED_LINES,
        global_memory=char_info or "（暂无角色信息）",
        recent_summary=prev_summary or "（故事开始）",
        sliding_window="（无前文）",
        current_task="撰写以下场景的正文",
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
