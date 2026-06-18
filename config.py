from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str
    ADMIN_IDS: List[int] = []

    # Database
    DATABASE_URL: str

    # Web App
    WEBAPP_URL: str = ""
    SECRET_KEY: str = "changeme"

    # Timezone
    TZ: str = "Asia/Tashkent"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # POSTGRES_DB/USER/PASSWORD kabi extra fieldlarni e'tiborsiz qoldirish
    )

    @field_validator("ADMIN_IDS", mode="before")
    @classmethod
    def parse_admin_ids(cls, v):
        """
        .env da ADMIN_IDS bir necha ko'rinishda bo'lishi mumkin:
          ADMIN_IDS=123456789
          ADMIN_IDS=123456789,987654321
          ADMIN_IDS=[123456789, 987654321]
        """
        if isinstance(v, (int, float)):
            return [int(v)]
        if isinstance(v, str):
            v = v.strip().strip("[]")
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        if isinstance(v, list):
            return [int(x) for x in v]
        return v


settings = Settings()
