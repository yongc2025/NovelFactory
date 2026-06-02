"""
场景编剧 — 将章节大纲拆解为具体、生动的场景
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


async def plan_scenes(
    project_id: str,
    chapter: dict,
    characters: list[dict] | None = None,
    params: dict | None = None,
) -> list[dict]:
    """
    为一章生成场景细纲

    Args:
        project_id: 项目 ID
        chapter: 章节大纲，包含 title, core_event, characters_present 等
        characters: 角色列表 (12维数据)
        params: 额外参数
    """
    logger.info("开始规划场景，章节: %s", chapter.get("title", "未知"))

    # 1. 组装角色深度信息
    char_info = "（暂无角色信息）"
    if characters:
        char_info = ""
        for c in characters:
            char_info += f"### {c.get('name', '未知')}\n"
            char_info += f"- 性格: {c.get('personality', '未知')}\n"
            char_info += f"- 核心欲望: {c.get('core_desire', c.get('desire', '未知'))}\n"
            char_info += f"- 核心矛盾: {c.get('fatal_flaw', '未知')}\n\n"

    # 2. 渲染 Prompt
    render_context = {
        "global_memory": char_info,
        "current_chapter": chapter,
        "chapter_title": chapter.get("title", "未知"),
        "chapter_content": chapter.get("core_event", ""),
    }

    system_prompt, user_prompt = skill_loader.render("scene", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
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

        # 数据标准化（Shim 层，对接前端接口）
        normalized_scenes = []
        for i, s in enumerate(scenes):
            if not isinstance(s, dict):
                continue

            num = s.get("number", s.get("scene_num", i + 1))

            # 提取描述：优先用 conflict，其次用 atmosphere，最后用 summary 或其他
            desc = s.get("description", "")
            if not desc:
                conflict = s.get("conflict", "")
                if isinstance(conflict, dict):
                    # 如果是复杂对象，尝试拼接
                    desc = f"{conflict.get('who_wants_what', '')} {conflict.get('who_blocks_whom', '')}"
                else:
                    desc = str(conflict)

            if not desc:
                desc = s.get("atmosphere", s.get("purpose", ""))

            # 映射为前端需要的字段
            normalized = {
                "scene_id": f"scene_{num}",
                "number": num,
                "title": f"场景 {num}: {s.get('location', '新场景')}",
                "description": desc,
                "location": s.get("location", "未知"),
                "status": "pending",
                **s  # 保留原始字段
            }
            normalized_scenes.append(normalized)

        logger.info("场景规划完成，共 %d 个场景", len(normalized_scenes))
        return normalized_scenes

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析场景失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
