"""
场景编剧 — 将章节大纲拆解为具体、生动的场景
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import SCENE_SYSTEM, SCENE_USER, render_prompt

logger = logging.getLogger(__name__)


async def plan_scenes(project_id: str, chapter: dict) -> list[dict]:
    """
    为一章生成场景细纲

    Args:
        project_id: 项目 ID
        chapter: 章节大纲，包含 title, core_event, characters_present 等

    Returns:
        场景列表
    """
    logger.info("开始规划场景，章节: %s", chapter.get("title", "未知"))

    user_prompt = render_prompt(
        SCENE_USER,
        chapter_title=chapter.get("title", "未知章节"),
        core_event=chapter.get("core_event", ""),
        characters_present=json.dumps(chapter.get("characters_present", []), ensure_ascii=False),
        emotion_position=chapter.get("emotion_position", ""),
        hook=chapter.get("hook", ""),
        foreshadow_ops=json.dumps(chapter.get("foreshadow_ops", []), ensure_ascii=False),
        character_states="（暂无角色状态信息）",
    )

    messages = [
        {"role": "system", "content": SCENE_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="scene", temperature=0.7, max_tokens=4096)

    return _parse_scenes(response)


def _parse_scenes(response: str) -> list[dict]:
    """解析场景 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        scenes = json.loads(json_str.strip())

        if isinstance(scenes, dict) and "scenes" in scenes:
            scenes = scenes["scenes"]

        if not isinstance(scenes, list):
            raise ValueError(f"期望列表，得到 {type(scenes)}")

        logger.info("场景规划完成，共 %d 个场景", len(scenes))
        return scenes

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析场景失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
