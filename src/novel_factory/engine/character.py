"""
角色设计师 — 创造立体、有记忆点的小说角色
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import CHARACTER_SYSTEM, CHARACTER_USER, render_prompt

logger = logging.getLogger(__name__)


async def design_characters(project_id: str, world: list[dict]) -> list[dict]:
    """
    设计角色

    Args:
        project_id: 项目 ID
        world: 世界观设定列表

    Returns:
        角色列表
    """
    logger.info("开始设计角色，项目: %s", project_id)

    world_summary = "\n".join(
        f"- {ws.get('category', '')}: {ws.get('content', '')[:100]}"
        for ws in world
    )

    user_prompt = render_prompt(
        CHARACTER_USER,
        title=project_id,
        genre="",
        premise="",
        world_summary=world_summary,
    )

    messages = [
        {"role": "system", "content": CHARACTER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="character", temperature=0.7, max_tokens=4096)

    return _parse_characters(response)


def _parse_characters(response: str) -> list[dict]:
    """解析角色 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        characters = json.loads(json_str.strip())

        # 兼容嵌套格式
        if isinstance(characters, dict):
            result = []
            for key in ["protagonist", "antagonist"]:
                if key in characters:
                    char = characters[key]
                    if isinstance(char, dict):
                        char["role"] = key
                        result.append(char)
            if "supporting" in characters and isinstance(characters["supporting"], list):
                result.extend(characters["supporting"])
            if result:
                characters = result

        if not isinstance(characters, list):
            raise ValueError(f"期望列表，得到 {type(characters)}")

        logger.info("角色设计完成，共 %d 个角色", len(characters))
        return characters

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析角色失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
