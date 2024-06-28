from pydantic_settings import BaseSettings
from asyncmy.cursors import DictCursor


class Settings(BaseSettings):
    # 기존 설정
    mysql_user: str
    mysql_password: str
    aes_key: str
    aes_iv: str
    smtp_server: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    secret_key: str

    # AWS Cognito 설정 추가
    aws_region: str
    cognito_user_pool_id: str
    cognito_client_id: str

    # MySQL 설정
    mysql_host: str
    mysql_user: str
    mysql_password: str
    mysql_database: str
    mysql_charset: str = 'utf8mb4'

    class Config:
        env_file = "../.env"


settings = Settings()

# MySQL 연결 설정
DB_CONFIG = {
    'host': settings.mysql_host,
    'user': settings.mysql_user,
    'password': settings.mysql_password,
    'db': settings.mysql_database,
    'charset': settings.mysql_charset,
    'cursorclass': DictCursor,
}

