from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: SecretStr
    weather_api_token: SecretStr
    model_config = SettingsConfigDict(
        env_file="resourses/.env", env_file_encoding="utf-8"
    )
