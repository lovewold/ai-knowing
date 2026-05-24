from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_root_env = Path(__file__).resolve().parent.parent.parent / ".env"
_local_env = Path(__file__).resolve().parent.parent / ".env"
_env_file = _root_env if _root_env.exists() else (_local_env if _local_env.exists() else ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_env_file), extra="ignore")

    database_url: str = "postgresql://aiknow:aiknow@localhost:5432/aiknow"
    redis_url: str = "redis://localhost:6379/0"
    config_dir: str = "../config"

    llm_provider: str = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"

    crawl_cron: str = "0 */2 * * *"
    report_language: str = "zh"
    auto_localize_on_crawl: bool = True
    localize_backlog_per_run: int = 30
    admin_token: str = ""  # 设置后管理 API 需 X-Admin-Token 头
    tavily_api_key: str = ""
    firecrawl_api_key: str = ""
    twitterapi_io_key: str = ""
    # embedding: local = 本地 fastembed（默认，无需 Key）；openai = 远程 API；auto = 有 Key 用 API 否则本地
    embedding_provider: str = "local"
    local_embedding_model: str = "BAAI/bge-small-zh-v1.5"
    embedding_api_key: str = ""
    embedding_base_url: str = "https://api.openai.com"
    embedding_model: str = "text-embedding-3-small"


settings = Settings()
