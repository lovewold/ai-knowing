from abc import ABC, abstractmethod

import httpx

from app.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        pass


class DeepSeekProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        models = [settings.deepseek_model]
        if settings.deepseek_model not in ("deepseek-chat", "deepseek-reasoner"):
            models.append("deepseek-chat")
        last_err: Exception | None = None
        async with httpx.AsyncClient(timeout=120) as client:
            for model in models:
                try:
                    resp = await client.post(
                        f"{settings.deepseek_base_url.rstrip('/')}/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {settings.deepseek_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": model,
                            "messages": [
                                {"role": "system", "content": system_prompt},
                                {"role": "user", "content": user_prompt},
                            ],
                            "temperature": 0.3,
                        },
                    )
                    resp.raise_for_status()
                    return resp.json()["choices"][0]["message"]["content"]
                except httpx.HTTPStatusError as e:
                    last_err = e
                    if e.response.status_code in (400, 404) and model != models[-1]:
                        continue
                    body = e.response.text[:300]
                    raise RuntimeError(f"LLM 请求失败 ({e.response.status_code}): {body}") from e
        if last_err:
            raise last_err
        raise RuntimeError("LLM 请求失败")


class OpenAIProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]


class AnthropicProvider(LLMProvider):
    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]
