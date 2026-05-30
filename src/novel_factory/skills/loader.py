"""
Prompt 加载器 — 从 skills/ 目录加载各角色的 SKILL.md

用法:
    from novel_factory.skills.loader import load_skill, render_skill

    # 加载原始模板
    template = load_skill("writer")

    # 渲染为最终 prompt（替换变量）
    prompt = render_skill("writer", global_memory="...", recent_summary="...")
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# skills 目录路径
SKILLS_DIR = Path(__file__).parent


def load_skill(role: str) -> str:
    """
    加载指定角色的 SKILL.md 内容

    Args:
        role: 角色名 (planner/worldbuilder/character/outliner/scene/writer/editor/metadata)

    Returns:
        SKILL.md 的完整内容

    Raises:
        FileNotFoundError: SKILL.md 不存在
    """
    skill_path = SKILLS_DIR / role / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(f"找不到角色技能文件: {skill_path}")

    content = skill_path.read_text(encoding="utf-8")
    logger.debug("加载角色技能: %s (%d 字符)", role, len(content))
    return content


def render_skill(role: str, **kwargs) -> str:
    """
    加载并渲染角色的 SKILL.md

    支持两种渲染方式：
    1. Jinja2 风格: {{ variable }}
    2. Python format 风格: {variable}

    Args:
        role: 角色名
        **kwargs: 要替换的变量

    Returns:
        渲染后的 prompt 文本
    """
    template = load_skill(role)

    # 先尝试 Jinja2 风格
    for key, value in kwargs.items():
        template = template.replace("{{ " + key + " }}", str(value))
        template = template.replace("{{" + key + "}}", str(value))

    return template


def list_skills() -> list[str]:
    """列出所有可用的角色技能"""
    skills = []
    for d in SKILLS_DIR.iterdir():
        if d.is_dir() and (d / "SKILL.md").exists():
            skills.append(d.name)
    return sorted(skills)
