"""
世界观架构师 — 构建完整、自洽的世界观设定
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import WORLDBUILDER_SYSTEM, WORLDBUILDER_USER, render_prompt

logger = logging.getLogger(__name__)


async def build_world(
    project_id: str,
    proposal: dict,
    params: dict | None = None,
) -> list[dict]:
    """
    构建世界观设定

    Args:
        project_id: 项目 ID
        proposal: 选题方案
        params: 项目创建参数，包含 world_setting/world_custom/forbidden_elements 等
    """
    params = params or {}
    logger.info("开始构建世界观，项目: %s", project_id)

    # 构建约束信息
    constraints = []
    if params.get("world_setting"):
        constraints.append(f"时空背景要求：{params['world_setting']}")
    if params.get("world_custom"):
        constraints.append(f"自定义世界观：{params['world_custom']}")
    if params.get("forbidden_elements"):
        constraints.append(f"禁忌元素（绝对不能出现）：{', '.join(params['forbidden_elements'])}")
    if params.get("reference_works"):
        constraints.append(f"参考作品风格：{params['reference_works']}")
    if params.get("target_audience") and params["target_audience"] != "general":
        audience = "女频读者" if params["target_audience"] == "female" else "男频读者"
        constraints.append(f"目标读者：{audience}")
    if params.get("feedback"):
        constraints.append(f"\n【用户反馈意见】：{params['feedback']}\n请根据以上反馈意见调整世界观设定。")

    constraint_text = "\n".join(constraints) if constraints else "（无特殊约束）"

    user_prompt = render_prompt(
        WORLDBUILDER_USER,
        title=proposal.get("title", "未命名"),
        genre=proposal.get("genre", params.get("genre_major", "")),
        premise=proposal.get("logline", proposal.get("premise", "")),
        target_readers=proposal.get("target_audience", proposal.get("target_readers", params.get("target_audience", "通用读者"))),
        platforms=proposal.get("platforms", ", ".join(params.get("platforms", ["番茄小说"]))),
    )
    user_prompt += f"\n\n创作约束：\n{constraint_text}"

    messages = [
        {"role": "system", "content": WORLDBUILDER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="worldbuilder", temperature=0.7, max_tokens=4096)

    return _parse_world(response)


def _parse_world(response: str) -> list[dict]:
    """解析世界观 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        world_settings = json.loads(json_str.strip())

        if isinstance(world_settings, dict):
            for key in ["world_settings", "settings", "world", "elements"]:
                if key in world_settings:
                    world_settings = world_settings[key]
                    break

        if not isinstance(world_settings, list):
            raise ValueError(f"期望列表，得到 {type(world_settings)}")

        for ws in world_settings:
            if "category" not in ws or "content" not in ws:
                raise ValueError(f"世界观设定缺少必要字段: {ws}")

        logger.info("世界观构建完成，共 %d 项设定", len(world_settings))
        return world_settings

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析世界观设定失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
