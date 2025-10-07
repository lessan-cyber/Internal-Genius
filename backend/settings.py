from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    A class to hold the application settings.
    """

    GOOGLE_API_KEY: str
    CHROMA_HOST: str = "chroma"
    CHROMA_PORT: int = 8000
    EMBEDDING_MODEL: str = "models/text-embedding-004"
    LLM_MODEL: str = "gemini-2.0-flash"
    TEMPERATURE: float = 0.3
    SYSTEM_PROMPT_PATH: str = "prompts/system_prompt.md"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Celery settings
    CELERY_CONFIG: dict = {
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,
        "task_track_started": True,
        "result_expires": 3600,
    }

    class Config:
        """
        A class to configure the settings.
        """

        env_file = ".env"


settings = Settings()
