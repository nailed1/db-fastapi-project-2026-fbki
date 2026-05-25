from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://hotel_user:hotel_pass@localhost:5432/hotel_db"
    secret_key: str = "change-me"
    debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    yookassa_shop_id: str = ""
    yookassa_secret_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
