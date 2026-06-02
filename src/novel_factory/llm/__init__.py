# novel_factory.llm — LLM 调用层
#
# gateway      : 与 DeepSeek API 通信的网关（重试、用量追踪、错误处理）
# skill_loader : 技能加载器，从 Markdown 加载和渲染 Prompts

from novel_factory.llm.gateway import complete
from novel_factory.llm.skill_loader import SkillLoader

__all__ = ["complete", "SkillLoader"]

