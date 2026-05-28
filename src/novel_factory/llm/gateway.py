"""
LLM 网关 -- 统一的大模型调用接口
支持 DeepSeek V3 / R1 及其他兼容 OpenAI 的模型
"""

import json
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_BASE_URL = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"  # V3
DEFAULT_TIMEOUT = 120


async def complete(
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    response_format: dict | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    调用 LLM 生成回复

    Args:
        messages: 对话消息列表，每条包含 role 和 content
        model: 模型名称，默认 deepseek-chat (V3)
        temperature: 温度参数，控制随机性
        max_tokens: 最大输出 token 数
        response_format: 响应格式，如 {"type": "json_object"}
        base_url: API 基础 URL，默认 DeepSeek
        api_key: API 密钥，默认从环境变量读取

    Returns:
        模型生成的文本内容

    Raises:
        httpx.HTTPStatusError: API 调用失败
        json.JSONDecodeError: JSON 解析失败
    """
    url = (base_url or DEFAULT_BASE_URL).rstrip("/") + "/chat/completions"
    key = api_key or os.getenv("DEEPSEEK_API_KEY", "")

    if not key:
        raise ValueError("未设置 DEEPSEEK_API_KEY 环境变量")

    payload: dict[str, Any] = {
        "model": model,
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
        logger.debug("LLM 调用: model=%s, messages=%d 条", model, len(messages))
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()

        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        logger.debug("LLM 返回: %d 字符", len(content))
        return content


async def complete_json(
    messages: list[dict[str, str]],
    model: str = DEFAULT_MODEL,
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
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
        **kwargs,
    )
    # 尝试从 markdown code block 中提取 JSON
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1].split("```")[0]
    return json.loads(content.strip())
