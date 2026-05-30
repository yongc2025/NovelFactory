"""
LLM 网关 -- 统一的大模型调用接口

支持多模型自动路由：
  - flash: DeepSeek V4 Flash (快速/低成本，默认)
  - pro:   DeepSeek V4 Pro (推理/复杂任务)
  - mimo:  MiMo V2.5 Pro (备选)

AI 角色 → 模型映射：
  - 大纲/世界观 → pro (需要推理)
  - 正文/场景   → flash (性价比高)
  - 校审/摘要   → flash (低温度精确)
"""

import json
import logging
import time
from typing import Any

import httpx

from novel_factory.config import settings

logger = logging.getLogger(__name__)

# 角色 → 默认模型提供者映射
ROLE_MODEL_MAP = {
    "planner": "flash",        # 策划经理
    "worldbuilder": "pro",     # 世界观架构师 (需要推理)
    "character": "flash",      # 角色设计师
    "outliner": "pro",         # 大纲编剧 (需要推理)
    "scene": "flash",          # 场景编剧
    "writer": "flash",         # 正文作者
    "editor_rules": "flash",   # 编辑审校-规则
    "editor_quality": "flash", # 编辑审校-质量
    "summary": "flash",        # 摘要生成
    "default": "flash",        # 默认
}

DEFAULT_TIMEOUT = 120

# 用量统计
_usage_log: list[dict] = []


async def complete(
    messages: list[dict[str, str]],
    role: str = "default",
    model: str | None = None,
    provider: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    response_format: dict | None = None,
) -> str:
    """
    调用 LLM 生成回复

    Args:
        messages: 对话消息列表
        role: AI 角色名 (用于自动选择模型)，如 planner/writer/editor
        model: 模型名称 (覆盖自动选择)
        provider: 模型提供者 (pro/flash/mimo)，覆盖角色映射
        temperature: 温度参数
        max_tokens: 最大输出 token 数
        response_format: 响应格式，如 {"type": "json_object"}

    Returns:
        模型生成的文本内容
    """
    # 确定使用哪个模型
    if model and provider:
        cfg = settings.get_model_config(provider)
        cfg["name"] = model
    elif provider:
        cfg = settings.get_model_config(provider)
    else:
        effective_provider = ROLE_MODEL_MAP.get(role, ROLE_MODEL_MAP["default"])
        cfg = settings.get_model_config(effective_provider)

    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    key = cfg["api_key"]
    model_name = model or cfg["name"]

    if not key:
        raise ValueError(f"未设置 API 密钥，请检查 .env 文件中的配置 (provider={provider or role})")

    payload: dict[str, Any] = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        logger.info("LLM 请求: role=%s, model=%s, messages=%d 条, max_tokens=%d", role, model_name, len(messages), max_tokens)
        logger.debug("LLM payload: %s", json.dumps(payload, ensure_ascii=False, indent=2)[:500])
        start_time = time.time()
        resp = await client.post(url, json=payload, headers=headers)
        elapsed = time.time() - start_time
        resp.raise_for_status()

        data = resp.json()

        # 提取 content (兼容不同响应格式)
        choice = data["choices"][0]
        message = choice.get("message", choice)
        content = message.get("content", "")

        # 用量统计
        usage = data.get("usage", {})
        _usage_log.append({
            "role": role,
            "model": model_name,
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
        })
        logger.info(
            "LLM 完成: role=%s, model=%s, %d 字符, tokens=%d/%d, 耗时=%.1fs",
            role, model_name, len(content),
            usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0),
            elapsed,
        )
        logger.debug("LLM 返回内容: %s", content[:300])

        return content


async def complete_json(
    messages: list[dict[str, str]],
    role: str = "default",
    model: str | None = None,
    provider: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    **kwargs,
) -> dict | list:
    """
    调用 LLM 并解析 JSON 响应

    Returns:
        解析后的 JSON 对象
    """
    content = await complete(
        messages=messages,
        role=role,
        model=model,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs,
    )
    # 尝试从 markdown code block 中提取 JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    return json.loads(content.strip())


def get_usage_summary() -> dict:
    """获取用量统计摘要"""
    total_input = sum(u["input_tokens"] for u in _usage_log)
    total_output = sum(u["output_tokens"] for u in _usage_log)
    by_role = {}
    for u in _usage_log:
        r = u["role"]
        if r not in by_role:
            by_role[r] = {"calls": 0, "input": 0, "output": 0}
        by_role[r]["calls"] += 1
        by_role[r]["input"] += u["input_tokens"]
        by_role[r]["output"] += u["output_tokens"]

    return {
        "total_calls": len(_usage_log),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "by_role": by_role,
    }
