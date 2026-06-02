"""
大纲编剧 — 设计紧凑、有节奏感的章节结构
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
    """
    params = params or {}
    logger.info("开始生成大纲，项目: %s，目标 %d 章", project_id, target_chapters)

    # 准备 SkillLoader 渲染上下文
    render_context = {
        "topic": topic,
        "characters": characters,
        "world": world,
        "target_chapters": target_chapters,
        "params": params,
    }

    system_prompt, user_prompt = skill_loader.render("outliner", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=16384)

    return _parse_outline(response, target_chapters)


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

        # 归一化伏笔 ID 和 结构
        for i, ch in enumerate(chapters, 1):
            if "chapter_num" not in ch:
                ch["chapter_num"] = ch.get("chapter_number", i)
            
            # 0021: 接口对齐 - 角色与描述
            if "characters_present" not in ch and "characters_involved" in ch:
                ch["characters_present"] = ch.pop("characters_involved")
            if "characters_present" not in ch and "characters" in ch:
                ch["characters_present"] = ch.pop("characters")
            
            # 0024: 情绪字段映射
            if "emotion_position" not in ch and "emotion_for_reader" in ch:
                ch["emotion_position"] = ch.get("emotion_for_reader")

            if "core_event" not in ch and "summary" in ch:
                ch["core_event"] = ch.get("summary")
            
            # 0023: 伏笔字段对齐
            if "foreshadowing" in ch and not ch.get("foreshadow_ops"):
                ch["foreshadow_ops"] = ch.pop("foreshadowing")
            
            # 处理 foreshadow_ops 结构化
            ops = ch.get("foreshadow_ops", [])
            normalized_ops = []
            for op in ops:
                if isinstance(op, str):
                    # 尝试解析 "埋设/plant：..." 或 "回收/callback：..."
                    action = "plant" if "埋" in op or "plant" in op.lower() else "callback"
                    content = op.split("：")[-1] if "：" in op else op
                    normalized_ops.append({"action": action, "content": content})
                else:
                    normalized_ops.append(op)
            ch["foreshadow_ops"] = normalized_ops

        # 归一化全局伏笔表
        for fs in foreshadows:
            if "id" not in fs:
                import uuid
                fs["id"] = str(uuid.uuid4())[:8]
            if "status" not in fs:
                fs["status"] = "planted"

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
        foreshadow_text = "\n### 已有伏笔池（供在后续章节进行 Callback/回收）：\n"
        for fs in existing_foreshadows:
            fs_id = fs.get("id") or fs.get("index") or "?"
            content = fs.get("content", "")
            planted = fs.get("chapter") or fs.get("planted_at_chapter") or "?"
            status = fs.get("status", "planted")
            foreshadow_text += f"- [ID: {fs_id}] {content} (埋于第{planted}章) | 状态: {status}\n"
        foreshadow_text += "\n请在后续章节的 foreshadow_ops 中引用上述 ID 进行 callback，或埋设新伏笔。\n"

    # 准备 SkillLoader 渲染上下文
    render_context = {
        "topic": topic,
        "characters": characters,
        "world": world,
        "target_chapters": batch_size,
        "start_chapter": start_chapter,
        "end_chapter": end_chapter,
        "params": params,
        "existing_context": existing_context,
        "foreshadow_text": foreshadow_text,
    }

    system_prompt, user_prompt = skill_loader.render("outliner", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=16384)


    response = await complete(messages=messages, role="outliner", temperature=0.7, max_tokens=16384)

    result = _parse_outline(response, batch_size)

    # 确保章节编号正确
    for i, ch in enumerate(result["chapters"]):
        ch["chapter_num"] = start_chapter + i

    return result["chapters"], result.get("foreshadows", [])
