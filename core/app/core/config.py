from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    GEMINI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_SUSPICIOUS_EXPORT_CHAT_ID: str
    SCHEDULER_TIMEZONE: str

    SUSPICIOUS_EXPORT_TEST_EVERY_MINUTE: bool = True
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    ML_ANALYSIS_QUEUE: str = "ml_analysis_queue"
    ML_RESULTS_QUEUE: str = "ml_results_queue"

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return self.DATABASE_URL.replace("+asyncpg", "")

    class Config:
        env_file = ".env"

settings = Settings()