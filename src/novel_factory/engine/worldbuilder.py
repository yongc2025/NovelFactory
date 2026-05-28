"""
世界观架构师 — 构建完整、自洽的世界观设定

职责：
1. 从时代背景、核心规则、势力分布、社会体系四个维度构建世界观
2. 确保世界观服务于故事冲突，而非堆砌设定
3. 将世界观设定存入数据库
"""

from __future__ import annotations

import json
import logging
import uuid

from novel_factory.db.connection import get_connection
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import WORLDBUILDER_SYSTEM, WORLDBUILDER_USER, render_prompt

logger = logging.getLogger(__name__)


async def build_world(project_id: str, proposal: dict) -> list[dict]:
    """
    构建世界观设定

    根据选题方案生成完整的世界观设定，包括：
    - 时代背景：时间、地点、历史阶段、社会环境
    - 核心规则：这个世界运转的底层逻辑
    - 势力分布：主要势力/阵营及其关系
    - 社会体系：阶层、经济、文化、权力结构

    Args:
        project_id: 项目 ID
        proposal: 选题方案，包含 title, genre, premise 等字段

    Returns:
        世界观设定列表
    """
    logger.info("开始构建世界观，项目: %s", project_id)

    user_prompt = render_prompt(
        WORLDBUILDER_USER,
        title=proposal.get("title", "未命名"),
        genre=proposal.get("genre", proposal.get("premise", "未知类型")),
        premise=proposal.get("premise", "未设定"),
        target_readers=proposal.get("target_readers", "通用读者"),
        platforms=proposal.get("platforms", "番茄小说"),
    )

    messages = [
        {"role": "system", "content": WORLDBUILDER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="worldbuilder", temperature=0.7, max_tokens=4096)

    return _parse_and_store_world(project_id, response)


def _parse_and_store_world(project_id: str, response: str) -> list[dict]:
    """解析世界观 JSON 并存入数据库"""
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

        with get_connection() as conn:
            for ws in world_settings:
                ws_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO world_settings (id, project_id, category, title, content) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (ws_id, project_id, ws["category"], ws.get("title", ws["category"]), ws["content"]),
                )
                ws["id"] = ws_id

        logger.info("世界观构建完成，共 %d 项设定", len(world_settings))
        return world_settings

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析世界观设定失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
