"""
世界观架构师 — 构建完整、自洽的世界观设定
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from novel_factory.llm.gateway import complete
from novel_factory.llm.skill_loader import SkillLoader

logger = logging.getLogger(__name__)

# 初始化 SkillLoader
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
skill_loader = SkillLoader(str(SKILLS_DIR))


async def build_world(
    project_id: str,
    proposal: dict,
    params: dict | None = None,
) -> dict:
    """
    构建世界观设定
    """
    params = params or {}
    logger.info("开始构建世界观，项目: %s", project_id)

    # 准备 SkillLoader 渲染上下文
    render_context = {
        "topic": proposal.get("title", "未命名"),
        "genre": proposal.get("genre", params.get("genre_major", "")),
        "theme": proposal.get("theme", ""),
        "params": params,
    }

    system_prompt, user_prompt = skill_loader.render("worldbuilder", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="worldbuilder", temperature=0.7, max_tokens=4096)

    return _parse_world(response)


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
    # 增加对 SKILL.md 中 System Prompt 指定字段的映射
    era = (
        world_data.get("era")
        or world_data.get("时代背景")
        or world_data.get("background")  # 映射 background
        or ""
    )
    geography = (
        world_data.get("geography")
        or world_data.get("地理环境")
        or world_data.get("势力分布")
        or world_data.get("background")  # 如果没有 era，把 background 也放这
        or ""
    )
    # 如果 era 和 geography 拿到了同样的内容（来自 background），则清理其中一个以避免重复显示
    if era == geography and len(era) > 0:
        era = "核心背景" 

    rules = _as_text_list(
        world_data.get("rules")
        or world_data.get("世界规则")
        or world_data.get("pressure_points")  # 映射压力点
    )
    constraints = _as_text_list(
        world_data.get("constraints")
        or world_data.get("约束条件")
        or world_data.get("unique_hooks")  # 映射独特卖点
    )

    return {
        "era": str(era),
        "geography": str(geography),
        "power_system": str(
            world_data.get("power_system")
            or world_data.get("核心规则")
            or world_data.get("力量体系")
            or ""
        ),
        "social_structure": str(
            world_data.get("social_structure")
            or world_data.get("社会结构")
            or world_data.get("社会体系")
            or ""
        ),
        "key_locations": _as_text_list(
            world_data.get("key_locations") or world_data.get("关键地点")
        ),
        "rules": rules,
        "constraints": constraints,
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
        res = []
        for item in value:
            if isinstance(item, dict):
                # 尝试提取名称和描述
                name = item.get("name") or item.get("title") or ""
                desc = item.get("description") or item.get("content") or ""
                if name and desc:
                    res.append(f"{name}: {desc}")
                elif name or desc:
                    res.append(str(name or desc))
            elif str(item).strip():
                res.append(str(item))
        return res
    if isinstance(value, str) and value.strip():
        return [value]
    return []
