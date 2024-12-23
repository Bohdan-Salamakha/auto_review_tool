import os


class Settings:
    """
    Setting of the application.
    Envs included in the __env_dict must be set in the .env file.
    """
    GITHUB_TOKEN = None
    OPENAI_API_KEY = None
    REDIS_URL = None

    RETRY_AFTER = 3600

    def __init__(self) -> None:
        from dotenv import load_dotenv

        load_dotenv()

        self.__env_dict = {}
        self.GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        self.__env_dict["GITHUB_TOKEN"] = self.GITHUB_TOKEN
        self.__env_dict["OPENAI_API_KEY"] = self.OPENAI_API_KEY

    @property
    def env_dict(self) -> dict:
        return self.__env_dict


settings = Settings()
