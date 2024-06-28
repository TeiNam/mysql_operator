from pydantic_settings import BaseSettings
from asyncmy.cursors import DictCursor
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    aes_key: str = os.environ.get("AES_KEY")
    aes_iv: str = os.environ.get("AES_IV")
    smtp_server: str = os.environ.get("SMTP_SERVER")
    smtp_port: int = os.environ.get("SMTP_PORT")
    smtp_username: str = os.environ.get("SMTP_USERNAME")
    smtp_password: str = os.environ.get("SMTP_PASSWORD")
    secret_key: str = os.environ.get("SECRET_KEY")
    aws_region: str = os.environ.get("AWS_REGION")
    cognito_user_pool_id: str = os.environ.get("COGNITO_USER_POOL_ID")
    cognito_client_id: str = os.environ.get("COGNITO_CLIENT_ID")
    mysql_host: str = os.environ.get("MYSQL_HOST")
    mysql_user: str = os.environ.get("MYSQL_USER")
    mysql_password: str = os.environ.get("MYSQL_PASSWORD")
    mysql_database: str = os.environ.get("MYSQL_DATABASE")


settings = Settings()

# MySQL 연결 설정
DB_CONFIG = {
    'host': settings.mysql_host,
    'user': settings.mysql_user,
    'password': settings.mysql_password,
    'db': settings.mysql_database,
    'cursorclass': DictCursor,
}

