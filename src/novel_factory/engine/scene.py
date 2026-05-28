"""
场景编剧 — 将章节大纲拆解为具体、生动的场景

职责：
1. 把每章大纲拆成 3-5 个场景
2. 为每个场景设计详细的场景卡
3. 确保场景之间有因果关系和情绪起伏
4. 将场景信息存入数据库
"""

from __future__ import annotations

import json
import logging
import uuid

from novel_factory.db.connection import get_connection
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import SCENE_SYSTEM, SCENE_USER, render_prompt

logger = logging.getLogger(__name__)


async def plan_scenes(project_id: str, chapter_id: str) -> list[dict]:
    """
    规划场景

    将章节大纲拆解为 3-5 个具体场景。

    Args:
        project_id: 项目 ID
        chapter_id: 章节 ID

    Returns:
        场景列表
    """
    logger.info("开始规划场景，章节: %s", chapter_id)

    with get_connection() as conn:
        chapter = conn.execute(
            "SELECT * FROM chapters WHERE id = ? AND project_id = ?",
            (chapter_id, project_id),
        ).fetchone()

        if not chapter:
            raise ValueError(f"章节不存在: {chapter_id}")

        characters = conn.execute(
            "SELECT name, role, personality_surface, current_state, voice_style "
            "FROM characters WHERE project_id = ?",
            (project_id,),
        ).fetchall()

    char_states = []
    for c in characters:
        char_states.append(
            f"- {c['name']}（{c['role'] or '未设定'}）: "
            f"{c['personality_surface'] or '未设定'}\n"
            f"  当前状态: {c['current_state'] or '故事开始'}\n"
            f"  说话风格: {c['voice_style'] or '未设定'}"
        )
    character_states = "\n".join(char_states) if char_states else "暂无角色信息"

    foreshadow_ops = chapter["foreshadow_ops"] or "无"

    user_prompt = render_prompt(
        SCENE_USER,
        chapter_title=chapter["title"] or "未命名",
        core_event=chapter["core_event"] or "未设定",
        characters_present=chapter["characters_present"] or "未设定",
        emotion_position=chapter["emotion_position"] or "未设定",
        hook=chapter["hook"] or "未设定",
        foreshadow_ops=foreshadow_ops,
        character_states=character_states,
    )

    messages = [
        {"role": "system", "content": SCENE_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="scene", temperature=0.7, max_tokens=4096)

    return _parse_and_store_scenes(project_id, chapter_id, response)


def _parse_and_store_scenes(project_id: str, chapter_id: str, response: str) -> list[dict]:
    """解析场景 JSON 并存入数据库"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        scenes = json.loads(json_str.strip())

        if isinstance(scenes, dict):
            for key in ["scenes", "场景"]:
                if key in scenes:
                    scenes = scenes[key]
                    break

        if not isinstance(scenes, list):
            raise ValueError(f"期望列表，得到 {type(scenes)}")

        with get_connection() as conn:
            for i, scene in enumerate(scenes):
                scene_id = str(uuid.uuid4())
                cp = scene.get("characters_present", [])
                cg = scene.get("character_goals", {})

                conn.execute(
                    "INSERT INTO scenes ("
                    "id, project_id, chapter_id, scene_num, location, "
                    "atmosphere, characters_present, character_goals, "
                    "conflict, turning_point, emotion_start, emotion_end, "
                    "dialogue_direction, sensory_details"
                    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        scene_id,
                        project_id,
                        chapter_id,
                        scene.get("number", i + 1),
                        scene.get("location"),
                        scene.get("atmosphere"),
                        json.dumps(cp, ensure_ascii=False) if isinstance(cp, list) else cp,
                        json.dumps(cg, ensure_ascii=False) if isinstance(cg, dict) else cg,
                        scene.get("conflict"),
                        scene.get("turning_point"),
                        scene.get("emotion_start"),
                        scene.get("emotion_end"),
                        scene.get("dialogue_direction"),
                        scene.get("sensory_details"),
                    ),
                )
                scene["id"] = scene_id

        logger.info("场景规划完成，共 %d 个场景", len(scenes))
        return scenes

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析场景数据失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
