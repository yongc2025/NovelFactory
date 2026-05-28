"""
策划经理 — 选题评估、题材推荐

职责：
1. 根据用户灵感和项目参数，生成 3-5 个可行的选题方案
2. 评估每个方案的市场潜力和可执行性
3. 输出结构化的选题方案供用户选择
"""

from __future__ import annotations

import json
import logging

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import PLANNER_SYSTEM, PLANNER_USER, render_prompt

logger = logging.getLogger(__name__)


async def generate_proposals(
    inspiration: str,
    genre_hint: str | None = None,
    params: dict | None = None,
) -> list[dict]:
    """
    生成选题方案

    Args:
        inspiration: 用户的灵感输入
        genre_hint: 题材提示
        params: 项目创建参数（来自 ProjectCreate），包含：
            - platforms: 目标平台
            - length_type: 篇幅定位
            - genre_major: 大类
            - genre_minor: 细分题材
            - target_audience: 目标读者
            - tone: 内容基调
            - protagonist_desc: 主角人设
            - world_setting: 世界观
            - reference_works: 参考作品
            - forbidden_elements: 禁忌元素

    Returns:
        选题方案列表
    """
    params = params or {}
    logger.info("开始生成选题方案，灵感: %s", inspiration[:50])

    # 构建丰富的上下文
    context_parts = [f"灵感：{inspiration}"]

    if genre_hint:
        context_parts.append(f"题材偏好：{genre_hint}")
    if params.get("genre_major"):
        context_parts.append(f"题材大类：{params['genre_major']}")
    if params.get("genre_minor"):
        context_parts.append(f"细分题材：{params['genre_minor']}")
    if params.get("target_audience") and params["target_audience"] != "general":
        audience = "女频" if params["target_audience"] == "female" else "男频"
        context_parts.append(f"目标读者：{audience}")
    if params.get("tone"):
        context_parts.append(f"内容基调：{params['tone']}")
    if params.get("platforms"):
        context_parts.append(f"目标平台：{', '.join(params['platforms'])}")
    if params.get("length_type"):
        length_map = {"short": "短篇(3000-8000字)", "medium": "中篇(5-20万字)", "long": "长篇(20万字以上)", "comic": "漫剧(60-100集)"}
        context_parts.append(f"篇幅定位：{length_map.get(params['length_type'], params['length_type'])}")
    if params.get("protagonist_desc"):
        context_parts.append(f"主角设定：{params['protagonist_desc']}")
    if params.get("world_setting"):
        context_parts.append(f"世界观：{params['world_setting']}")
    if params.get("reference_works"):
        context_parts.append(f"参考作品：{params['reference_works']}")
    if params.get("forbidden_elements"):
        context_parts.append(f"禁忌元素：{', '.join(params['forbidden_elements'])}")

    genre_text = "\n".join(context_parts[1:])  # 除灵感外的所有上下文

    user_prompt = render_prompt(
        PLANNER_USER,
        inspiration=inspiration,
        genre_hint=genre_text,
    )

    messages = [
        {"role": "system", "content": PLANNER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="planner", temperature=0.7, max_tokens=4096)

    return _parse_proposals(response)


def _parse_proposals(response: str) -> list[dict]:
    """解析 LLM 返回的选题方案 JSON"""
    try:
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]

        proposals = json.loads(json_str.strip())

        if isinstance(proposals, dict):
            for key in ["proposals", "plans", "options", "results"]:
                if key in proposals:
                    proposals = proposals[key]
                    break

        if not isinstance(proposals, list):
            raise ValueError(f"期望列表，得到 {type(proposals)}")

        for p in proposals:
            for field in ["title", "premise", "score"]:
                if field not in p:
                    p[field] = "未设定" if field != "score" else 5
            if not isinstance(p["score"], (int, float)):
                p["score"] = 5
            p["score"] = max(1, min(10, p["score"]))

        proposals.sort(key=lambda x: x.get("score", 0), reverse=True)
        logger.info("生成了 %d 个选题方案", len(proposals))
        return proposals

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析选题方案失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
