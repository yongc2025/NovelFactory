# novel_factory.llm — LLM 调用层
#
# gateway  : 与 DeepSeek API 通信的网关（重试、用量追踪、错误处理）
# prompts  : 各 AI 角色的 Jinja2 system-prompt 模板

from novel_factory.llm.gateway import complete
from novel_factory.llm.prompts import render_prompt

__all__ = ["complete", "render_prompt"]
