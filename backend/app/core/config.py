from pydantic_settings import BaseSettings


class Settings(BaseSettings):
  app_name: str = "Kanban Visual API"
  environment: str = "development"
  database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/kanban_db"

  model_config = {
    "env_file": ".env",
    "env_file_encoding": "utf-8",
  }


settings = Settings()

