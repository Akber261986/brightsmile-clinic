"""Application settings loaded from environment / .env."""

from __future__ import annotations
from dotenv import load_dotenv
from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "BrightSmile Chatbot Agent"
    supabase_url: str = ""
    supabase_secret_key: str = ""
    resend_api_key: str = ""
    receptionist_email: str = "reception@brightsmileclinic.com"
    sender_email: str = "BrightSmile Clinic <onboarding@resend.dev>"

    gemini_api_key: str = 
    openai_api_key: str = ""
    llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_model: str = "gemini-3.5-flash"

    @property
    def db_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key)

    @property
    def email_configured(self) -> bool:
        return bool(self.resend_api_key)

    @property
    def llm_api_key(self) -> str:
        return self.gemini_api_key or self.openai_api_key

    @property
    def llm_configured(self) -> bool:
        return bool(self.llm_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
    