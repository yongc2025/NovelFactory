"""
大纲编剧 — 设计紧凑、有节奏感的章节结构
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import OUTLINER_SYSTEM, OUTLINER_USER, render_prompt

logger = logging.getLogger(__name__)


async def generate_outline(
    project_id: str,
    topic: dict,
    world: list[dict],
    characters: list[dict],
    target_chapters: int = 10,
) -> dict:
    """
    生成章节大纲

    Args:
        project_id: 项目 ID
        topic: 选题方案
        world: 世界观设定
        characters: 角色列表
        target_chapters: 目标章节数

    Returns:
        {"chapters": [...], "foreshadows": [...]}
    """
    logger.info("开始生成大纲，项目: %s，目标 %d 章", project_id, target_chapters)

    characters_summary = "\n".join(
        f"- {c.get('name', '未知')}: {c.get('role', '')}, {c.get('personality', '')}"
        for c in characters
    )
    world_summary = "\n".join(
        f"- {ws.get('category', '')}: {ws.get('content', '')[:80]}"
        for ws in world
    )

    user_prompt = render_prompt(
        OUTLINER_USER,
        title=topic.get("title", "未命名"),
        genre=topic.get("genre", ""),
        premise=topic.get("premise", ""),
        word_count=topic.get("word_count", "8000"),
        characters_summary=characters_summary,
        world_summary=world_summary,
        target_chapters=target_chapters,
    )

    messages = [
        {"role": "system", "content": render_prompt(OUTLINER_SYSTEM, target_chapters=target_chapters)},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=8192)

    return _parse_outline(response, target_chapters)


def _parse_outline(response: str, target_chapters: int) -> dict:
    """解析大纲 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        # 兼容不同格式
        if isinstance(data, list):
            data = {"chapters": data}

        chapters = data.get("chapters", [])
        foreshadows = data.get("foreshadows", [])

        # 给每章加上 chapter_num
        for i, ch in enumerate(chapters, 1):
            if "chapter_num" not in ch:
                ch["chapter_num"] = i

        logger.info("大纲生成完成，共 %d 章，%d 个伏笔", len(chapters), len(foreshadows))
        return {"chapters": chapters, "foreshadows": foreshadows}

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析大纲失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
