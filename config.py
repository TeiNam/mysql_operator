from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mysql_user: str
    mysql_password: str
    aes_key: str
    aes_iv: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    secret_key: str

    class Config:
        env_file = ".env"


settings = Settings()
