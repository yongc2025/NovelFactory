"""
角色设计师 — 创造立体、有记忆点的小说角色
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import CHARACTER_SYSTEM, CHARACTER_USER, render_prompt

logger = logging.getLogger(__name__)


async def design_characters(
    project_id: str,
    world: list[dict] | dict,
    params: dict | None = None,
) -> list[dict]:
    """
    设计角色

    Args:
        project_id: 项目 ID
        world: 世界观设定列表
        params: 项目创建参数，包含角色预设
    """
    params = params or {}
    logger.info("开始设计角色，项目: %s", project_id)

    world_summary = _format_world_summary(world)

    # 构建角色约束
    constraints = []
    if params.get("protagonist_name"):
        constraints.append(f"主角名：{params['protagonist_name']}")
    if params.get("protagonist_desc"):
        constraints.append(f"主角人设：{params['protagonist_desc']}")
    if params.get("antagonist_name"):
        constraints.append(f"反派名：{params['antagonist_name']}")
    if params.get("antagonist_desc"):
        constraints.append(f"反派人设：{params['antagonist_desc']}")
    if params.get("has_romance") and params["has_romance"] != "flexible":
        constraints.append(f"CP线：{'需要' if params['has_romance'] == 'yes' else '不需要'}")
    if params.get("romance_desc"):
        constraints.append(f"CP设定：{params['romance_desc']}")
    if params.get("supporting_count"):
        constraints.append(f"配角数量：{params['supporting_count']}个")
    if params.get("target_audience") and params["target_audience"] != "general":
        audience = "女频" if params["target_audience"] == "female" else "男频"
        constraints.append(f"目标读者：{audience}")
    if params.get("feedback"):
        constraints.append(f"\n【用户反馈意见】：{params['feedback']}\n请根据以上反馈意见调整角色设定。")

    constraint_text = "\n".join(constraints) if constraints else "（无特殊约束）"

    user_prompt = render_prompt(
        CHARACTER_USER,
        title=project_id,
        genre=params.get("genre_major", ""),
        premise=params.get("premise", ""),
        world_summary=world_summary,
    )
    user_prompt += f"\n\n角色约束：\n{constraint_text}"

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


def _format_world_summary(world: list[dict] | dict) -> str:
    """将新旧世界观结构格式化为角色生成可读摘要。"""
    if isinstance(world, dict):
        parts = [
            ("时代背景", world.get("era")),
            ("地理环境", world.get("geography")),
            ("力量体系", world.get("power_system")),
            ("社会结构", world.get("social_structure")),
            ("关键地点", "；".join(str(item) for item in world.get("key_locations", []))),
            ("世界规则", "；".join(str(item) for item in world.get("rules", []))),
            ("约束条件", "；".join(str(item) for item in world.get("constraints", []))),
        ]
        return "\n".join(f"- {label}: {value}" for label, value in parts if value)

    return "\n".join(
        f"- {ws.get('category', '')}: {str(ws.get('content', ''))[:100]}"
        for ws in world
    )
