import httpx
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.models import LlmModelConfig


class DynamicLLMProvider:
    def __init__(self, config: LlmModelConfig):
        self.config = config

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        cfg = self.config
        provider = cfg.provider.lower()
        if provider == "anthropic":
            return await self._anthropic(cfg, system_prompt, user_prompt)
        return await self._openai_compatible(cfg, system_prompt, user_prompt)

    async def _openai_compatible(self, cfg: LlmModelConfig, system: str, user: str) -> str:
        if cfg.base_url:
            base = cfg.base_url.rstrip("/")
        elif cfg.provider == "deepseek":
            base = "https://api.deepseek.com"
        else:
            base = "https://api.openai.com"
        url = f"{base}/v1/chat/completions"
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {cfg.api_key or ''}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": cfg.model_id,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    "temperature": cfg.temperature,
                    "max_tokens": cfg.max_tokens,
                },
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def _anthropic(self, cfg: LlmModelConfig, system: str, user: str) -> str:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": cfg.api_key or "",
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json={
                    "model": cfg.model_id,
                    "max_tokens": cfg.max_tokens,
                    "system": system,
                    "messages": [{"role": "user", "content": user}],
                    "temperature": cfg.temperature,
                },
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]


def resolve_model_config(db: Session | None, task: str = "report", model_id: int | None = None) -> LlmModelConfig | None:
    if db is None:
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            return _resolve(db, task, model_id)
        finally:
            db.close()
    return _resolve(db, task, model_id)


def _resolve(db: Session, task: str, model_id: int | None) -> LlmModelConfig | None:
    if model_id:
        return db.query(LlmModelConfig).filter(LlmModelConfig.id == model_id, LlmModelConfig.enabled == True).first()  # noqa: E712
    tagged = (
        db.query(LlmModelConfig)
        .filter(LlmModelConfig.enabled == True)  # noqa: E712
        .all()
    )
    for m in tagged:
        tags = [t.strip() for t in (m.task_tags or "").split(",") if t.strip()]
        if task in tags:
            return m
    default = db.query(LlmModelConfig).filter(LlmModelConfig.is_default == True, LlmModelConfig.enabled == True).first()  # noqa: E712
    if default:
        return default
    return db.query(LlmModelConfig).filter(LlmModelConfig.enabled == True).first()  # noqa: E712


def get_llm_provider(task: str = "report", model_id: int | None = None, db: Session | None = None):
    """Resolve LLM from DB config; fallback to legacy env-based providers."""
    cfg = resolve_model_config(db, task, model_id)
    if cfg and cfg.api_key:
        return DynamicLLMProvider(cfg)
    from app.llm.provider import AnthropicProvider, DeepSeekProvider, OpenAIProvider
    provider = settings.llm_provider.lower()
    if provider == "openai":
        return OpenAIProvider()
    if provider == "anthropic":
        return AnthropicProvider()
    return DeepSeekProvider()
