"""
大纲编剧 — 设计紧凑、有节奏感的章节结构

职责：
1. 生成章节大纲，包含完整的情节线、情绪弧线、伏笔操作
2. 生成伏笔部署表，确保伏笔有明确的埋设和回收点
3. 将大纲和伏笔存入数据库
"""

from __future__ import annotations

import json
import logging
import uuid

from novel_factory.db.connection import get_connection
from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import OUTLINER_SYSTEM, OUTLINER_USER, render_prompt

logger = logging.getLogger(__name__)


async def generate_outline(
    project_id: str,
    target_chapters: int = 10,
) -> list[dict]:
    """
    生成章节大纲

    Args:
        project_id: 项目 ID
        target_chapters: 目标章节数，默认 10 章

    Returns:
        章节大纲列表
    """
    logger.info("开始生成大纲，项目: %s，目标章节数: %d", project_id, target_chapters)

    with get_connection() as conn:
        project = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()

        if not project:
            raise ValueError(f"项目不存在: {project_id}")

        characters = conn.execute(
            "SELECT name, role, personality_surface, core_desire, arc_start "
            "FROM characters WHERE project_id = ?",
            (project_id,),
        ).fetchall()

        world_settings = conn.execute(
            "SELECT category, content FROM world_settings WHERE project_id = ?",
            (project_id,),
        ).fetchall()

    char_summaries = []
    for c in characters:
        char_summaries.append(
            f"- {c['name']}（{c['role'] or '未设定'}）: "
            f"{c['personality_surface'] or '未设定'}\n"
            f"  核心欲望: {c['core_desire'] or '未设定'}\n"
            f"  角色弧光: {c['arc_start'] or '未设定'}"
        )
    characters_summary = "\n".join(char_summaries) if char_summaries else "暂无角色信息"

    world_summaries = []
    for ws in world_settings:
        world_summaries.append(f"【{ws['category']}】{ws['content']}")
    world_summary = "\n\n".join(world_summaries) if world_summaries else "暂无世界观设定"

    system_prompt = render_prompt(OUTLINER_SYSTEM, target_chapters=target_chapters)
    user_prompt = render_prompt(
        OUTLINER_USER,
        title=project["title"],
        genre=project["genre"] or "未设定",
        premise=project.get("premise") or "未设定",
        word_count=project.get("target_words") or "未设定",
        characters_summary=characters_summary,
        world_summary=world_summary,
        target_chapters=target_chapters,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=8192)

    return _parse_and_store_outline(project_id, response)


def _parse_and_store_outline(project_id: str, response: str) -> list[dict]:
    """解析大纲 JSON 并存入数据库"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        if isinstance(data, dict):
            chapters = data.get("chapters", [])
            foreshadows = data.get("foreshadows", [])
        elif isinstance(data, list):
            chapters = data
            foreshadows = []
        else:
            raise ValueError(f"期望 dict 或 list，得到 {type(data)}")

        if not isinstance(chapters, list):
            raise ValueError(f"章节数据格式错误: {type(chapters)}")

        with get_connection() as conn:
            for i, ch in enumerate(chapters):
                ch_id = str(uuid.uuid4())
                cp = ch.get("characters_present", [])
                fo = ch.get("foreshadow_ops", [])
                plp = ch.get("plot_lines_progress", {})

                conn.execute(
                    "INSERT INTO chapters ("
                    "id, project_id, chapter_num, title, outline, core_event, "
                    "characters_present, emotion_position, emotion_arc, "
                    "hook, foreshadow_ops, plot_lines_progress"
                    ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        ch_id,
                        project_id,
                        i + 1,
                        ch.get("title"),
                        ch.get("core_event"),  # outline
                        ch.get("core_event"),
                        json.dumps(cp, ensure_ascii=False) if isinstance(cp, list) else cp,
                        ch.get("emotion_position"),
                        json.dumps(ch.get("emotion_arc", {}), ensure_ascii=False)
                        if isinstance(ch.get("emotion_arc"), dict) else ch.get("emotion_arc"),
                        ch.get("hook"),
                        json.dumps(fo, ensure_ascii=False) if isinstance(fo, list) else fo,
                        json.dumps(plp, ensure_ascii=False) if isinstance(plp, dict) else plp,
                    ),
                )
                ch["id"] = ch_id
                ch["number"] = i + 1

            for fs in foreshadows:
                fs_id = str(uuid.uuid4())
                chapter_id = None
                if "chapter" in fs:
                    for ch in chapters:
                        if ch.get("number") == fs["chapter"]:
                            chapter_id = ch["id"]
                            break

                conn.execute(
                    "INSERT INTO foreshadows ("
                    "id, project_id, content, planted_chapter, "
                    "target_chapter, status"
                    ") VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        fs_id,
                        project_id,
                        fs.get("content", ""),
                        fs.get("planted_chapter"),
                        fs.get("target_chapter"),
                        fs.get("status", "planted"),
                    ),
                )
                fs["id"] = fs_id

        logger.info("大纲生成完成，共 %d 章，%d 个伏笔", len(chapters), len(foreshadows))
        return chapters

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析大纲数据失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
