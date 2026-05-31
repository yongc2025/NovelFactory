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
    world: list[dict] | dict,
    characters: list[dict],
    target_chapters: int = 10,
    params: dict | None = None,
) -> dict:
    """
    生成章节大纲

    Args:
        project_id: 项目 ID
        topic: 选题方案
        world: 世界观设定
        characters: 角色列表
        target_chapters: 目标章节数
        params: 项目创建参数，包含节奏/爽点/伏笔等策略
    """
    params = params or {}
    logger.info("开始生成大纲，项目: %s，目标 %d 章", project_id, target_chapters)

    characters_summary = "\n".join(
        f"- {c.get('name', '未知')}: {c.get('role', '')}, {c.get('personality', '')}"
        for c in characters
    )
    world_summary = _format_world_summary(world)

    # 构建节奏约束
    rhythm_parts = []
    if params.get("climax_density"):
        density_map = {"high": "高密度爽点（每1-2章一个小爽点）", "medium": "中等密度（每3-4章一个小爽点）", "low": "低密度（重铺垫，每5-6章一个爽点）"}
        rhythm_parts.append(f"爽点密度：{density_map.get(params['climax_density'], params['climax_density'])}")
    if params.get("climax_interval"):
        rhythm_parts.append(f"每{params['climax_interval']}章安排一个小爽点")
    if params.get("foreshadow_count"):
        rhythm_parts.append(f"埋设{params['foreshadow_count']}个伏笔")
    if params.get("tone"):
        rhythm_parts.append(f"内容基调：{params['tone']}")
    if params.get("chapter_word_range"):
        rhythm_parts.append(f"每章字数：{params['chapter_word_range'][0]}-{params['chapter_word_range'][1]}字")
    if params.get("feedback"):
        rhythm_parts.append(f"\n【用户反馈意见】：{params['feedback']}\n请根据以上反馈意见调整大纲。")

    rhythm_text = "\n".join(rhythm_parts) if rhythm_parts else ""

    user_prompt = render_prompt(
        OUTLINER_USER,
        title=topic.get("title", "未命名"),
        genre=topic.get("genre", params.get("genre_major", "")),
        premise=topic.get("logline", topic.get("premise", "")),
        word_count=params.get("target_words", topic.get("word_count", "8000")),
        characters_summary=characters_summary,
        world_summary=world_summary,
        target_chapters=target_chapters,
    )
    if rhythm_text:
        user_prompt += f"\n\n节奏与策略要求：\n{rhythm_text}"

    messages = [
        {"role": "system", "content": render_prompt(OUTLINER_SYSTEM, target_chapters=target_chapters)},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=16384)

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

        if isinstance(data, list):
            data = {"chapters": data}

        chapters = data.get("chapters", [])
        foreshadows = data.get("foreshadows", [])

        for i, ch in enumerate(chapters, 1):
            if "chapter_num" not in ch:
                ch["chapter_num"] = i

        logger.info("大纲生成完成，共 %d 章，%d 个伏笔", len(chapters), len(foreshadows))
        return {"chapters": chapters, "foreshadows": foreshadows}

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析大纲失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e


def _format_world_summary(world: list[dict] | dict) -> str:
    """将新旧世界观结构格式化为大纲生成可读摘要。"""
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
        f"- {ws.get('category', '')}: {str(ws.get('content', ''))[:80]}"
        for ws in world
    )


async def generate_outline_batch(
    project_id: str,
    topic: dict,
    world: list[dict] | dict,
    characters: list[dict],
    start_chapter: int,
    batch_size: int,
    params: dict | None = None,
) -> tuple[list[dict], list[dict]]:
    """
    分批生成大纲

    Args:
        project_id: 项目 ID
        topic: 选题方案
        world: 世界观设定
        characters: 角色列表
        start_chapter: 起始章节号
        batch_size: 本批生成章节数
        params: 项目参数

    Returns:
        (new_chapters, new_foreshadows) 元组
    """
    params = params or {}
    end_chapter = start_chapter + batch_size - 1
    logger.info("开始分批生成大纲，项目: %s，第 %d-%d 章", project_id, start_chapter, end_chapter)

    characters_summary = "\n".join(
        f"- {c.get('name', '未知')}: {c.get('role', '')}, {c.get('personality', '')}"
        for c in characters
    )
    world_summary = _format_world_summary(world)

    # 构建节奏约束
    rhythm_parts = []
    chapter_word_count = params.get("chapter_word_count", 3000)
    rhythm_parts.append(f"每章目标字数：{chapter_word_count}字（允许±100字浮动）")
    if params.get("climax_density"):
        density_map = {"high": "高密度爽点（每1-2章一个小爽点）", "medium": "中等密度（每3-4章一个小爽点）", "low": "低密度（重铺垫，每5-6章一个爽点）"}
        rhythm_parts.append(f"爽点密度：{density_map.get(params['climax_density'], params['climax_density'])}")
    if params.get("tone"):
        rhythm_parts.append(f"内容基调：{params['tone']}")
    if params.get("feedback"):
        rhythm_parts.append(f"\n【用户反馈意见】：{params['feedback']}\n请根据以上反馈意见调整大纲。")

    rhythm_text = "\n".join(rhythm_parts) if rhythm_parts else ""

    # 已有章节上下文
    existing_context = params.get("existing_chapters_context", "")
    existing_foreshadows = params.get("existing_foreshadows", [])
    foreshadow_text = ""
    if existing_foreshadows:
        foreshadow_text = "\n已有伏笔：\n" + "\n".join(
            f"- {f.get('content', '')}（埋设于第{f.get('chapter', '?')}章）"
            for f in existing_foreshadows
        )

    user_prompt = render_prompt(
        OUTLINER_USER,
        title=topic.get("title", "未命名"),
        genre=topic.get("genre", params.get("genre_major", "")),
        premise=topic.get("logline", topic.get("premise", "")),
        word_count=params.get("target_words", topic.get("word_count", "8000")),
        characters_summary=characters_summary,
        world_summary=world_summary,
        target_chapters=batch_size,
    )

    # 添加上下文信息
    context_parts = []
    if existing_context:
        context_parts.append(existing_context)
    if foreshadow_text:
        context_parts.append(foreshadow_text)
    if rhythm_text:
        context_parts.append(f"节奏与策略要求：\n{rhythm_text}")
    context_parts.append(f"\n请从第 {start_chapter} 章开始生成 {batch_size} 章大纲。")
    context_parts.append(f"章节编号从 {start_chapter} 到 {end_chapter}。")

    user_prompt += "\n\n" + "\n".join(context_parts)

    messages = [
        {"role": "system", "content": render_prompt(OUTLINER_SYSTEM, target_chapters=batch_size)},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=16384)

    result = _parse_outline(response, batch_size)

    # 确保章节编号正确
    for i, ch in enumerate(result["chapters"]):
        ch["chapter_num"] = start_chapter + i

    return result["chapters"], result.get("foreshadows", [])
