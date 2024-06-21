import jwt
from datetime import timedelta, datetime
from config import settings

SECRET_KEY = settings.secret_key


def create_email_token(email: str):
    expiration = datetime.utcnow() + timedelta(hours=2)
    token = jwt.encode({"email": email, "exp": expiration}, SECRET_KEY, algorithm="HS256")
    return token


def verify_email_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
