import os
from pathlib import Path

from dotenv import load_dotenv


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        env = os.getenv("TEST_ENV", "dev")
        env_file = Path(__file__).parent / "environments" / f"{env}.env"
        if env_file.exists():
            load_dotenv(env_file)

        self.BASE_URL = os.getenv("BASE_URL", "https://restful-booker.herokuapp.com")
        self.AUTH_USERNAME = os.getenv("AUTH_USERNAME", "admin")
        self.AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "password123")
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
        self.RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
        self.RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    def __repr__(self):
        return (
            f"Settings(base_url={self.BASE_URL}, "
            f"timeout={self.REQUEST_TIMEOUT}, env={os.getenv('TEST_ENV', 'dev')})"
        )


settings = Settings()
