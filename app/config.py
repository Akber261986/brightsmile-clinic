"""Application settings loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BrightSmile Chatbot Agent"
    supabase_url: str = ""
    supabase_secret_key: str = ""
    resend_api_key: str = ""
    receptionist_email: str = "reception@brightsmileclinic.com"
    sender_email: str = "BrightSmile Clinic <onboarding@resend.dev>"

    @property
    def db_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key)

    @property
    def email_configured(self) -> bool:
        return bool(self.resend_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()