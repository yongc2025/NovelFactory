"""
策划经理 — 选题评估、题材推荐

职责：
1. 根据用户灵感输入，生成 3-5 个可行的选题方案
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
) -> list[dict]:
    """
    生成选题方案

    根据用户的灵感输入，生成 3-5 个可行的选题方案。
    每个方案包含完整的市场分析和执行建议。

    Args:
        inspiration: 用户的灵感输入，可以是关键词、一句话描述、甚至情绪
        genre_hint: 可选的题材提示，如"重生复仇"、"甜宠"等

    Returns:
        选题方案列表，每个方案包含：
        - title: 标题（吸引眼球）
        - premise: 一句话前提（核心冲突+卖点）
        - target_readers: 目标读者画像
        - word_count: 建议字数
        - platforms: 推荐平台（小红书/番茄/两者皆可）
        - score: 综合评分（1-10）
        - reasoning: 评分理由（市场分析+可执行性）
    """
    logger.info("开始生成选题方案，灵感: %s", inspiration[:50])

    genre_text = f"题材偏好：{genre_hint}\n" if genre_hint else ""

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

        # 处理包装格式
        if isinstance(proposals, dict):
            for key in ["proposals", "plans", "options", "results"]:
                if key in proposals:
                    proposals = proposals[key]
                    break

        if not isinstance(proposals, list):
            raise ValueError(f"期望列表，得到 {type(proposals)}")

        # 验证字段
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
