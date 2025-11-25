from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str = ""  
    DB_HOST: str
    DB_PORT: int = 3306
    DB_NAME: str

    @property
    def CONNECTION_STRING(self) -> str:
        if self.DB_PASSWORD:
            return f"mysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            return f"mysql://{self.DB_USER}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


print(settings.CONNECTION_STRING)
