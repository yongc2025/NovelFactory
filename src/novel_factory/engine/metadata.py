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

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import METADATA_SYSTEM, METADATA_USER, render_prompt

logger = logging.getLogger(__name__)

# 番茄小说分类体系（用于分类匹配参考）
CATEGORY_TREE = {
    "男频": {
        "玄幻": ["东方玄幻", "异世大陆", "高武世界", "远古神话", "王朝争霸", "升级练功"],
        "仙侠": ["修真文明", "幻想修仙", "神话修真", "洪荒封神"],
        "都市": ["都市生活", "都市异能", "都市修真", "商战职场", "娱乐明星", "青春校园"],
        "历史": ["架空历史", "历史传记", "秦汉三国", "上古先秦", "两晋隋唐", "五代十国", "两宋元明"],
        "军事": ["军事战争", "战争幻想", "抗战烽火", "谍战特工"],
        "游戏": ["游戏生涯", "虚拟网游", "电子竞技", "游戏异界"],
        "体育": ["篮球运动", "体育赛事", "足球运动", "竞技乒乓"],
        "科幻": ["超级科技", "时空穿梭", "未来世界", "古武机甲", "星际文明"],
        "灵异": ["灵异奇谈", "恐怖惊悚", "悬疑探险", "风水秘术"],
        "奇幻": ["剑与魔法", "史诗奇幻", "黑暗幻想", "现代魔法"],
    },
    "女频": {
        "古代言情": ["宫斗宅斗", "穿越奇情", "古代情缘", "女尊王朝", "经商种田"],
        "现代言情": ["豪门总裁", "都市情缘", "婚恋情缘", "职场丽人", "娱乐明星"],
        "浪漫青春": ["青春校园", "青梅竹马", "纯爱初恋", "叛逆成长"],
        "仙侠奇缘": ["仙侣奇缘", "武侠情缘", "古典仙侠", "幻想异界"],
        "悬疑灵异": ["灵异奇谈", "推理悬疑", "探险生存", "恐怖惊悚"],
        "玄幻言情": ["异世大陆", "远古神话", "高武世界", "玄幻仙侠"],
        "科幻空间": ["时空穿梭", "未来世界", "星际恋歌", "超级科技"],
        "游戏竞技": ["网游情缘", "电子竞技", "游戏异界"],
    },
}


async def generate_metadata(
    project_id: str,
    topic: dict,
    outline: dict,
    characters: list | dict,
    params: dict,
) -> dict:
    """
    生成书籍元数据

    Args:
        project_id: 项目 ID
        topic: 选题方案
        outline: 章节大纲
        characters: 角色列表或字典
        params: 项目参数（来自 ProjectCreate）

    Returns:
        书籍元数据字典，包含 title, title_candidates, synopsis_short/medium/long,
        tags, category, category_path
    """
    logger.info("开始生成书籍元数据，项目: %s", project_id)

    # 提取上下文信息
    topic_text = json.dumps(topic, ensure_ascii=False, indent=2) if topic else "{}"
    outline_summary = _summarize_outline(outline)
    protagonist = _extract_protagonist(characters)
    genre = _build_genre_text(params)
    platforms = ", ".join(params.get("platforms", ["fanqie"]))
    target_audience = _audience_label(params.get("target_audience", "female"))

    # 用户偏好（来自 ProjectCreate 的 book_* 字段）
    user_title = params.get("book_title") or "无"
    user_synopsis = params.get("book_synopsis") or "无"
    user_tags = ", ".join(params.get("book_tags", [])) if params.get("book_tags") else "无"
    user_category = params.get("book_category") or "无"

    user_prompt = render_prompt(
        METADATA_USER,
        topic=topic_text,
        outline_summary=outline_summary,
        protagonist=protagonist,
        genre=genre,
        platforms=platforms,
        target_audience=target_audience,
        user_title=user_title,
        user_synopsis=user_synopsis,
        user_tags=user_tags,
        user_category=user_category,
    )

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
