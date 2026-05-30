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
) -> dict:
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


def _parse_world(response: str) -> dict:
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

        if isinstance(world_settings, dict):
            normalized = _normalize_world_object(world_settings)
            logger.info("世界观构建完成，字段数: %d", len(normalized))
            return normalized

        if isinstance(world_settings, list):
            normalized = _normalize_world_list(world_settings)
            logger.info("世界观构建完成，共 %d 项设定", len(world_settings))
            return normalized

        raise ValueError(f"期望对象或列表，得到 {type(world_settings)}")

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析世界观设定失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e


def _normalize_world_object(world_data: dict) -> dict:
    """将世界观对象补齐为前端展示所需字段。"""
    return {
        "era": str(world_data.get("era") or world_data.get("时代背景") or ""),
        "geography": str(world_data.get("geography") or world_data.get("地理环境") or world_data.get("势力分布") or ""),
        "power_system": str(world_data.get("power_system") or world_data.get("核心规则") or world_data.get("力量体系") or ""),
        "social_structure": str(world_data.get("social_structure") or world_data.get("社会结构") or world_data.get("社会体系") or ""),
        "key_locations": _as_text_list(world_data.get("key_locations") or world_data.get("关键地点")),
        "rules": _as_text_list(world_data.get("rules") or world_data.get("世界规则")),
        "constraints": _as_text_list(world_data.get("constraints") or world_data.get("约束条件")),
    }


def _normalize_world_list(world_list: list[dict]) -> dict:
    """兼容旧版 [{category, content}] 世界观格式。"""
    result = {
        "era": "",
        "geography": "",
        "power_system": "",
        "social_structure": "",
        "key_locations": [],
        "rules": [],
        "constraints": [],
    }
    category_map = {
        "时代背景": "era",
        "地理环境": "geography",
        "势力分布": "geography",
        "核心规则": "power_system",
        "力量体系": "power_system",
        "社会体系": "social_structure",
        "社会结构": "social_structure",
    }
    for item in world_list:
        if "category" not in item or "content" not in item:
            raise ValueError(f"世界观设定缺少必要字段: {item}")
        category = str(item.get("category", ""))
        content = str(item.get("content", ""))
        key = category_map.get(category)
        if key:
            result[key] = content
        if "地点" in category or "势力" in category:
            result["key_locations"].append(content)
        if "规则" in category or "体系" in category:
            result["rules"].append(content)
        if "约束" in category or "限制" in category or "禁忌" in category:
            result["constraints"].append(content)
    if not result["constraints"] and result["social_structure"]:
        result["constraints"].append(result["social_structure"])
    return result


def _as_text_list(value: object) -> list[str]:
    """将模型返回的列表/字符串规范为字符串列表。"""
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value]
    return []
