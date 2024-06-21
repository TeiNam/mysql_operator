from fastapi import APIRouter, HTTPException, Depends
from pydantic import EmailStr
from models.user import UserCreate, User
from modules.database import get_db, Database
from modules.email import send_email
from modules.jwt_util import create_email_token, verify_email_token
from modules.crypto_util import encrypt_password, decrypt_password

router = APIRouter()


@router.post("/signup/", response_model=User)
async def signup(user: UserCreate, db: Database = Depends(get_db)):
    encrypted_password = encrypt_password(user.password)
    email_token = create_email_token(user.email)
    query = """
    INSERT INTO user (email, password, permission, is_use, is_auth, email_token)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    await db.execute(query, user.email, encrypted_password, 1, 'Y', 'N', email_token)

    # 이메일 인증 링크 발송
    email_body = f"Please click the link to verify your email: http://yourdomain.com/api/verify-email?token={email_token}"
    send_email(user.email, "Verify your email", email_body)

    return {"user_id": 1, "email": user.email, "permission": 1, "is_use": "Y", "is_auth": "N"}  # 실제로는 생성된 ID를 반환해야 합니다.


@router.get("/verify-email/")
async def verify_email(token: str, db: Database = Depends(get_db)):
    email = verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    query = "UPDATE user SET is_auth = 'Y', email_token = NULL WHERE email = %s"
    result = await db.execute(query, email)
    if result.rowcount == 0:
        raise HTTPException(status_code=400, detail="User not found")

    return {"message": "Email verified successfully"}


@router.post("/login/")
async def login(user: UserCreate, db: Database = Depends(get_db)):
    query = "SELECT user_id, password, is_auth, email_token FROM user WHERE email = %s"
    db_user = await db.fetch_one(query, user.email)
    if db_user:
        if db_user['is_auth'] != 'Y':
            email = verify_email_token(db_user['email_token'])
            if not email:  # 토큰이 만료된 경우 새 토큰을 생성하고 이메일 발송
                new_email_token = create_email_token(user.email)
                update_query = "UPDATE user SET email_token = %s WHERE email = %s"
                await db.execute(update_query, new_email_token, user.email)
                email_body = f"Please click the link to verify your email: http://yourdomain.com/api/verify-email?token={new_email_token}"
                send_email(user.email, "Verify your email", email_body)
                raise HTTPException(status_code=403,
                                    detail="Please verify your email. A new verification link has been sent.")
            raise HTTPException(status_code=403, detail="Please verify your email first")
        stored_password = decrypt_password(db_user['password'])
        if stored_password and stored_password == user.password:
            return {"access_token": "your_token"}  # JWT 토큰을 반환하는 로직을 추가해야 합니다.
    raise HTTPException(status_code=400, detail="Invalid credentials")
