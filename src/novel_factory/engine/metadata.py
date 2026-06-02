"""
元数据生成器 — 书名/简介/标签/分类

职责：
1. 根据选题+大纲+角色生成5个候选书名
2. 生成3个版本的简介（50/150/300字）
3. 推荐5个标签
4. 匹配番茄小说分类体系
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


async def generate_metadata(
    project_id: str,
    topic: dict,
    outline: dict,
    characters: list | dict,
    params: dict,
) -> dict:
    """
    生成书籍元数据
    """
    logger.info("开始生成书籍元数据，项目: %s", project_id)

    # 提取上下文
    outline_summary = _summarize_outline(outline)
    protagonist = _extract_protagonist(characters)
    genre = _build_genre_text(params)
    platforms = ", ".join(params.get("platforms", ["fanqie"]))

    # 准备 SkillLoader 渲染上下文
    render_context = {
        "topic": topic,
        "outline_summary": outline_summary,
        "protagonist": protagonist,
        "genre": genre,
        "platforms": platforms,
        "user_preferences": {
            "title": params.get("book_title"),
            "synopsis": params.get("book_synopsis"),
            "tags": params.get("book_tags"),
            "category": params.get("book_category"),
        }
    }

    system_prompt, user_prompt = skill_loader.render("metadata", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="metadata", temperature=0.7, max_tokens=4096)

    return _parse_metadata(response)


    messages = [
        {"role": "system", "content": METADATA_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="planner", temperature=0.8, max_tokens=4096)

    return _parse_metadata(response)


def _summarize_outline(outline: dict) -> str:
    """从大纲中提取摘要信息"""
    if not outline:
        return "暂无大纲"

    chapters = outline.get("chapters", [])
    if not chapters:
        return json.dumps(outline, ensure_ascii=False)[:500]

    summary_parts = []
    for ch in chapters[:5]:  # 最多取前5章
        ch_num = ch.get("chapter_num", "?")
        title = ch.get("title", "")
        core = ch.get("core_event", "")
        summary_parts.append(f"第{ch_num}章 {title}: {core}")

    if len(chapters) > 5:
        summary_parts.append(f"...共{len(chapters)}章")

    return "\n".join(summary_parts)


def _extract_protagonist(characters: list | dict) -> str:
    """提取主角信息"""
    if isinstance(characters, dict):
        # 可能是 {"protagonist": {...}} 格式
        if "protagonist" in characters:
            char = characters["protagonist"]
            return f"{char.get('name', '未命名')} - {char.get('personality', '')} - {char.get('core_desire', '')}"
        # 也可能是普通字典
        return json.dumps(characters, ensure_ascii=False)[:300]

    if isinstance(characters, list):
        for char in characters:
            if char.get("role") == "protagonist":
                return f"{char.get('name', '未命名')} - {char.get('personality', '')} - {char.get('core_desire', '')}"
        # 没找到主角，返回第一个
        if characters:
            char = characters[0]
            return f"{char.get('name', '未命名')} - {char.get('personality', '')} - {char.get('core_desire', '')}"

    return "暂无角色信息"


def _build_genre_text(params: dict) -> str:
    """构建题材描述文本"""
    parts = []
    if params.get("genre_major"):
        parts.append(params["genre_major"])
    if params.get("genre_minor"):
        parts.append(params["genre_minor"])
    if params.get("tone"):
        parts.append(f"基调: {params['tone']}")
    return " > ".join(parts) if parts else "通用"


def _audience_label(audience: str) -> str:
    """读者标签转中文"""
    mapping = {"female": "女频", "male": "男频", "general": "通用"}
    return mapping.get(audience, "通用")


def _parse_metadata(response: str) -> dict:
    """解析 LLM 返回的元数据 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        metadata = json.loads(json_str.strip())

        # 如果返回的是嵌套结构，尝试提取
        if isinstance(metadata, dict) and "metadata" in metadata:
            metadata = metadata["metadata"]

        # 确保所有必需字段存在
        result = {
            "title": metadata.get("title", "未命名"),
            "title_candidates": metadata.get("title_candidates", []),
            "synopsis_short": metadata.get("synopsis_short", ""),
            "synopsis_medium": metadata.get("synopsis_medium", ""),
            "synopsis_long": metadata.get("synopsis_long", ""),
            "tags": metadata.get("tags", []),
            "category": metadata.get("category", ""),
            "category_path": metadata.get("category_path", ""),
        }

        # 补齐不足5个的候选书名
        while len(result["title_candidates"]) < 5:
            result["title_candidates"].append(result["title"])

        # 补齐不足5个的标签
        while len(result["tags"]) < 5:
            result["tags"].append("")

        logger.info("元数据生成完成: 书名=%s, 标签=%s", result["title"], result["tags"])
        return result

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析元数据失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
