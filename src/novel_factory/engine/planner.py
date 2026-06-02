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
from pathlib import Path

from novel_factory.llm.gateway import complete
from novel_factory.llm.skill_loader import SkillLoader

logger = logging.getLogger(__name__)

# 初始化 SkillLoader
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
skill_loader = SkillLoader(str(SKILLS_DIR))


async def generate_proposals(
    inspiration: str,
    genre_hint: str | None = None,
    params: dict | None = None,
) -> list[dict]:
    """
    生成选题方案
    """
    params = params or {}
    logger.info("开始生成选题方案，灵感: %s", inspiration[:50])

    # 使用 SkillLoader 渲染
    render_context = {
        "inspiration": inspiration,
        "genre_hint": genre_hint or "未指定",
        "params": params,
    }

    system_prompt, user_prompt = skill_loader.render("planner", render_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    response = await complete(messages=messages, role="planner", temperature=0.7, max_tokens=4096)

    return _parse_proposals(response)


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
            # 确保必填字段存在
            defaults = {
                "title": "未命名",
                "logline": "",
                "theme": "",
                "genre": "",
                "target_audience": "",
                "conflict": "",
                "hook": "",
                "platforms": [],
                "word_count": "",
                "score": 50,
                "reasoning": "",
            }
            for field, default_val in defaults.items():
                if field not in p:
                    p[field] = default_val
            # 评分规范化
            if not isinstance(p["score"], (int, float)):
                p["score"] = 50
            # 兼容旧格式 1-10 分 -> 1-100 分
            if p["score"] <= 10:
                p["score"] = round(p["score"] * 10)
            p["score"] = max(1, min(100, p["score"]))
            # platforms 规范化
            if isinstance(p["platforms"], str):
                p["platforms"] = [p["platforms"]]

        proposals.sort(key=lambda x: x.get("score", 0), reverse=True)
        logger.info("生成了 %d 个选题方案", len(proposals))
        return proposals

    except (json.JSONDecodeError, IndexError, ValueError) as e:
        logger.error("解析选题方案失败: %s", e)
        raise ValueError(f"LLM 返回的 JSON 格式错误: {e}") from e
