"""
正文作者 — 根据场景细纲生成正文
"""

from __future__ import annotations

import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import (
    CONTENT_RED_LINES,
    STYLE_INSTRUCTION,
    WRITER_SYSTEM,
    WRITER_USER,
    render_prompt,
)

logger = logging.getLogger(__name__)


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

    Args:
        project_id: 项目 ID
        chapter: 章节大纲
        scene: 场景细纲
        characters: 角色列表
        prev_summary: 前文摘要
        params: 项目创建参数，包含 tone/style_sample/chapter_word_range 等
    """
    params = params or {}
    logger.info("开始生成正文，场景: %s", scene.get("location", "未知"))

    # 角色信息
    char_info = ""
    if characters:
        char_info = "\n".join(
            f"- {c.get('name', '未知')}: {c.get('personality', '')}, 说话风格: {c.get('speaking_style', c.get('voice_style', ''))}"
            for c in characters
        )

    # 场景大纲
    scene_outline = f"""
章节: {chapter.get('title', '')}
场景地点: {scene.get('location', '')}
氛围: {scene.get('atmosphere', '')}
出场角色: {', '.join(scene.get('characters_present', []))}
冲突: {scene.get('conflict', '')}
转折: {scene.get('turning_point', '')}
情绪: {scene.get('emotion_start', '')} → {scene.get('emotion_end', '')}
对话方向: {scene.get('dialogue_direction', '')}
感官细节: {scene.get('sensory_details', '')}
""".strip()

    # 额外风格指令
    extra_style = ""
    if params.get("tone"):
        tone_map = {
            "爽文": "节奏要快，爽点密集，打脸要狠，读者看了要喊爽",
            "虐文": "情感要细腻，虐心要到位，但虐中要有甜，不能纯虐",
            "甜文": "甜度要高，细节要暖，让人看了嘴角上扬",
            "悬疑": "悬念要层层递进，每段都要有信息量，让人猜不到下一步",
            "热血": "节奏紧凑，战斗场面要有画面感，燃点要到位",
        }
        extra_style += f"\n基调要求：{tone_map.get(params['tone'], params['tone'])}"
    if params.get("style_sample"):
        extra_style += f"\n参考风格样本（模仿这种写作风格）：\n{params['style_sample'][:500]}"
    if params.get("chapter_word_range"):
        lo, hi = params["chapter_word_range"]
        extra_style += f"\n本章目标字数：{lo}-{hi}字"
    if params.get("target_audience") and params["target_audience"] != "general":
        audience = "女频读者（注重情感细腻度、角色心理描写）" if params["target_audience"] == "female" else "男频读者（注重爽感、节奏、实力展现）"
        extra_style += f"\n目标读者：{audience}"

    # 0019: 滑动窗口 — 读上一章 draft 末尾作为连接上下文
    sliding_window = "（无前文）"
    try:
        ch_num = chapter.get("chapter_num", 0) if isinstance(chapter, dict) else 0
        if ch_num and ch_num > 1:
            from novel_factory.api.deps import get_store
            store = get_store()
            prev_draft = store.get_draft(project_id, ch_num - 1)
            if prev_draft and isinstance(prev_draft, str):
                tail = prev_draft.strip()[-400:]
                if tail:
                    sliding_window = f"【上一章结尾】\n{tail}"
    except Exception as e:
        logger.warning("读取滑动窗口失败: %s", e)

    system_prompt = render_prompt(
        WRITER_SYSTEM,
        style_instruction=STYLE_INSTRUCTION + extra_style,
        content_red_lines=CONTENT_RED_LINES,
        global_memory=char_info or "（暂无角色信息）",
        recent_summary=prev_summary or "（故事开始）",
        sliding_window=sliding_window,
        current_task="撰写以下场景的正文",
    )

    user_prompt = render_prompt(
        WRITER_USER,
        scene_outline=scene_outline,
        character_info=char_info or "（暂无）",
    )

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
