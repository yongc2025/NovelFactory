"""
角色设计师 — 创造立体、有记忆点的小说角色

职责：
1. 生成主角、反派、2-3个配角的完整角色卡
2. 确保角色之间有化学反应和冲突关系
3. 为每个角色设计清晰的成长弧光
4. 将角色信息存入数据库
"""

from __future__ import annotations

import json
import logging
import uuid

from novel_factory.db.connection import get_connection
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import CHARACTER_SYSTEM, CHARACTER_USER, render_prompt

logger = logging.getLogger(__name__)


async def design_characters(
    project_id: str,
    world_settings: list[dict],
) -> list[dict]:
    """
    设计角色

    根据世界观设定生成完整的角色卡，包括：
    - 1个主角：有清晰的成长弧光
    - 1个反派：有合理的动机，不是纯粹的恶
    - 2-3个配角：各有特色，服务于主线

    Args:
        project_id: 项目 ID
        world_settings: 世界观设定列表

    Returns:
        角色列表
    """
    logger.info("开始设计角色，项目: %s", project_id)

    with get_connection() as conn:
        project = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()

        if not project:
            raise ValueError(f"项目不存在: {project_id}")

    world_summary = "\n".join(
        f"【{ws['category']}】{ws['content'][:100]}..."
        for ws in world_settings
    )

    user_prompt = render_prompt(
        CHARACTER_USER,
        title=project["title"],
        genre=project["genre"] or "未设定",
        premise=project.get("premise") or "未设定",
        world_summary=world_summary,
    )

    messages = [
        {"role": "system", "content": CHARACTER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="character", temperature=0.7, max_tokens=4096)

    return _parse_and_store_characters(project_id, response)


def _parse_and_store_characters(project_id: str, response: str) -> list[dict]:
    """解析角色 JSON 并存入数据库"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        characters = json.loads(json_str.strip())

        if isinstance(characters, dict):
            for key in ["characters", "角色", "cast"]:
                if key in characters:
                    characters = characters[key]
                    break

        if not isinstance(characters, list):
            raise ValueError(f"期望列表，得到 {type(characters)}")

        # 角色名映射
        role_map = {"主角": "protagonist", "反派": "antagonist", "配角": "supporting"}

        with get_connection() as conn:
            for char in characters:
                char_id = str(uuid.uuid4())
                role = char.get("role", "supporting")
                role = role_map.get(role, role)

                conn.execute(
                    "INSERT INTO characters ("
                    "id, project_id, name, role, age, appearance, "
                    "personality_surface, personality_deep, "
                    "core_desire, core_fear, voice_style, secret, "
                    "arc_start, arc_end, current_state, relation_summary"
                    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        char_id,
                        project_id,
                        char["name"],
                        role,
                        char.get("age"),
                        char.get("appearance"),
                        char.get("personality"),  # personality_surface
                        char.get("personality_deep"),
                        char.get("core_desire"),
                        char.get("core_fear"),
                        char.get("speaking_style"),  # voice_style
                        char.get("twist_point"),  # secret
                        char.get("arc_description"),  # arc_start
                        char.get("arc_end"),
                        char.get("current_state"),
                        char.get("relationship_to_protagonist"),  # relation_summary
                    ),
                )
                char["id"] = char_id
                char["role"] = role

        logger.info("角色设计完成，共 %d 个角色", len(characters))
        return characters

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析角色数据失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
