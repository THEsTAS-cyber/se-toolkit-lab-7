"""Bot configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    model_config = SettingsConfigDict(env_file=".env.bot.secret", extra="ignore")

    bot_token: str | None = None
    lms_api_base_url: str | None = None
    lms_api_key: str | None = None
    llm_api_model: str = "coder-model"
    llm_api_key: str | None = None
    llm_api_base_url: str | None = None


settings = BotSettings()
