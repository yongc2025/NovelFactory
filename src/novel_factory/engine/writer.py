"""
正文作者 — 根据场景细纲生成正文
"""

from __future__ import annotations

import logging
from pathlib import Path

from novel_factory.llm.gateway import complete
from novel_factory.llm.skill_loader import SkillLoader

logger = logging.getLogger(__name__)

# 初始化 SkillLoader
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
skill_loader = SkillLoader(str(SKILLS_DIR))


async def write_scene(
    project_id: str,
    chapter: dict,
    scene: dict,
    characters: list[dict] | None = None,
    prev_summary: str = "",
    params: dict | None = None,
) -> str:
    """
    为一个场景生成正文
    """
    params = params or {}
    logger.info("开始生成正文，场景: %s", scene.get("location", "未知"))

    # 0023: 提取伏笔指令
    foreshadow_ops = chapter.get("foreshadow_ops", [])
    ops_str = "（本章无伏笔指令）"
    if foreshadow_ops:
        ops_str = ""
        for op in foreshadow_ops:
            action_cn = "【埋设】" if op.get("action") == "plant" else "【回收/呼应】"
            ops_str += f"- {action_cn}: {op.get('content')}\n"

    # 1. 组装角色深度信息 (12维数据)
    char_info = "（暂无角色信息）"
    if characters:
        char_info = ""
        for c in characters:
            char_info += f"### {c.get('name', '未知')}\n"
            char_info += f"- 性格: {c.get('personality', '未知')}\n"
            char_info += f"- 核心欲望: {c.get('core_desire', c.get('desire', '未知'))}\n"
            char_info += f"- 核心恐惧: {c.get('core_fear', '未知')}\n"
            char_info += f"- 致命弱点: {c.get('fatal_flaw', '未知')}\n"
            char_info += f"- 说话风格: {c.get('speaking_style', c.get('voice_style', '未知'))}\n"
            char_info += f"- 弧光描述: {c.get('arc_description', '未知')}\n\n"

    # 2. 组装当前任务上下文
    current_task = {
        "chapter_title": chapter.get("title", ""),
        "chapter_num": chapter.get("chapter_num", 0),
        "scene_location": scene.get("location", ""),
        "atmosphere": scene.get("atmosphere", ""),
        "characters_present": scene.get("characters_present", []),
        "conflict": scene.get("conflict", ""),
        "turning_point": scene.get("turning_point", ""),
        "emotion_start": scene.get("emotion_start", ""),
        "emotion_end": scene.get("emotion_end", ""),
        "dialogue_direction": scene.get("dialogue_direction", ""),
        "sensory_details": scene.get("sensory_details", ""),
    }

    # 3. 滑动窗口 (短期记忆)
    sliding_window = "（无前文）"
    try:
        ch_num = chapter.get("chapter_num", 0)
        if ch_num and ch_num > 1:
            from novel_factory.db.project_store import ProjectStore
            store = ProjectStore()
            prev_draft = store.get_draft(project_id, ch_num - 1)
            if prev_draft:
                tail = prev_draft.strip()[-600:]
                sliding_window = f"【上一章结尾】\n{tail}"
    except Exception as e:
        logger.warning("读取滑动窗口失败: %s", e)

    # 4. 使用 SkillLoader 渲染 Prompt
    render_context = {
        "global_memory": char_info,
        "recent_summary": prev_summary or "（故事开始）",
        "foreshadow_ops": ops_str,
        "sliding_window": sliding_window,
        "current_task": current_task,
        "chapter_index": chapter.get("chapter_num", 0),
        "scene_index": scene.get("number", 1),
        "target_word_count": params.get("target_word_count", 1000),
    }
    
    system_prompt, user_prompt = skill_loader.render("writer", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 5. 调用大模型
    draft = await complete(messages=messages, role="writer", temperature=0.85, max_tokens=4096)

    logger.info("正文生成完成，约 %d 字", len(draft))
    return draft


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    draft = await complete(messages=messages, role="writer", temperature=0.85, max_tokens=4096)

    logger.info("正文生成完成，约 %d 字", len(draft))
    return draft


async def revise_with_feedback(
    project_id: str,
    chapter: dict,
    original_draft: str,
    characters: list[dict] | None = None,
    review_issues: list[dict] | None = None,
    user_feedback: str = "",
    params: dict | None = None,
) -> str:
    """根据审校意见和用户反馈修改正文

    Args:
        project_id: 项目 ID
        chapter: 章节大纲
        original_draft: 原正文
        characters: 角色列表
        review_issues: 审校发现的问题
        user_feedback: 用户反馈
        params: 项目参数
    """
    params = params or {}
    logger.info("开始修改正文，章节: %s", chapter.get("title", "未知"))

    char_info = ""
    if characters:
        char_info = "\n".join(
            f"- {c.get('name', '未知')}: {c.get('personality', '')}, 说话风格: {c.get('speaking_style', c.get('voice_style', ''))}"
            for c in characters
        )

    issues_text = ""
    if review_issues:
        issues_text = "\n".join(
            f"- [{issue.get('severity', 'warning')}] {issue.get('type', '')}: {issue.get('detail', '')}"
            for issue in review_issues
        )

    system_prompt = """你是一位网文作者，负责根据审校意见修改正文。

修改要求：
1. 针对审校指出的问题逐一修复
2. 保持角色性格一致性
3. 保持原文的节奏和风格
4. 如果用户提供了反馈意见，优先满足用户需求
5. 不要大幅改变原文结构，只修改有问题的部分
6. 输出修改后的完整正文"""

    user_prompt = f"""章节：{chapter.get('title', '')}
核心事件：{chapter.get('core_event', '')}

角色信息：
{char_info or '（暂无）'}

审校问题：
{issues_text or '（无）'}

用户反馈：
{user_feedback or '（无）'}

原正文：
{original_draft}"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    revised = await complete(messages=messages, role="writer", temperature=0.7, max_tokens=4096)
    logger.info("正文修改完成，约 %d 字", len(revised))
    return revised
