"""
角色设计师 — 创造立体、有记忆点的小说角色
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


async def design_characters(
    project_id: str,
    world: list[dict] | dict,
    params: dict | None = None,
) -> list[dict]:
    """
    设计角色
    """
    params = params or {}
    logger.info("开始设计角色，项目: %s", project_id)

    world_summary = _format_world_summary(world)

    # 准备 SkillLoader 渲染上下文
    render_context = {
        "topic": {
            "title": project_id,
            "genre": params.get("genre_major", ""),
            "premise": params.get("premise", ""),
        },
        "world_summary": world_summary,
        "params": params,
    }

    system_prompt, user_prompt = skill_loader.render("character", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="character", temperature=0.7, max_tokens=4096)

    return _parse_characters(response)


    response = await complete(messages=messages, role="character", temperature=0.7, max_tokens=4096)

    return _parse_characters(response, project_id)


def _parse_characters(response: str, project_id: str = "") -> list[dict]:
    """解析角色 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        characters = json.loads(json_str.strip())

        if isinstance(characters, dict):
            # 兼容字典格式: {"protagonist": {...}, "antagonist": {...}, "supporting": [...]}
            result = []
            if "protagonist" in characters:
                char = characters["protagonist"]
                if isinstance(char, dict):
                    char["role"] = "protagonist"
                    result.append(char)
            if "antagonist" in characters:
                char = characters["antagonist"]
                if isinstance(char, dict):
                    char["role"] = "antagonist"
                    result.append(char)
            if "supporting" in characters and isinstance(characters["supporting"], list):
                for char in characters["supporting"]:
                    if isinstance(char, dict):
                        char["role"] = "supporting"
                        result.append(char)
            if result:
                characters = result

        if not isinstance(characters, list):
            raise ValueError(f"期望列表，得到 {type(characters)}")

        # 统一和补全字段
        for i, char in enumerate(characters):
            # 基础字段
            char.setdefault("id", f"char_{i+1}")
            char.setdefault("project_id", project_id)
            
            # 角色映射与归一化
            raw_role = str(char.get("role", "")).lower()
            if not raw_role or any(x in raw_role for x in ["主角", "男一", "女一", "protagonist"]):
                char["role"] = "protagonist"
            elif any(x in raw_role for x in ["反派", "反一", "antagonist", "boss"]):
                char["role"] = "antagonist"
            else:
                char["role"] = "supporting"
            
            # 即使归一化了角色，也可以把原始详细定位存在描述里
            if "role_detail" not in char:
                char["role_detail"] = char.get("role", "")

            # 灵魂属性映射 (根据 web/src/types/index.ts 和 LLM 常见输出)
            if "core_wound" in char and "wound" not in char:
                char["wound"] = char.get("core_wound")
            if "wound" not in char:
                char["wound"] = char.get("core_wound", "")

            if "desire" in char and "core_desire" not in char:
                char["core_desire"] = char.pop("desire")
            if "fear" in char and "core_fear" not in char:
                char["core_fear"] = char.pop("fear")
            
            # 补齐 background (如果为空则用 personality 或 arc_description 填充)
            if not char.get("background"):
                char["background"] = char.get("personality", "")[:100] + "..." if len(char.get("personality", "")) > 100 else char.get("personality", "")

            # 列表字段兜底
            char.setdefault("traits", [])
            char.setdefault("relationships", [])
            
            # 处理 relationship_with_protagonist 这种扁平字段
            if "relationship_with_protagonist" in char and not char["relationships"]:
                if char["role"] != "protagonist":
                    # 尝试找到主角名字
                    protagonist = next((c for c in characters if c.get("role") == "protagonist"), None)
                    p_name = protagonist.get("name", "主角") if protagonist else "主角"
                    char["relationships"].append({
                        "target_id": "char_1",
                        "target_name": p_name,
                        "relation": "对手/伙伴",
                        "description": char.pop("relationship_with_protagonist")
                    })

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
