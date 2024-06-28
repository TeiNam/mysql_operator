from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import aioboto3
from modules.mysql_connector import MySQLConnector
from config import settings

router = APIRouter()
security = HTTPBearer()


class UserRequest(BaseModel):
    username: str
    email: str
    password: str


class LoginUser(BaseModel):
    username: str
    password: str


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    async with aioboto3.Session().client('cognito-idp', region_name=settings.aws_region) as cognito:
        try:
            response = await cognito.get_user(
                AccessToken=credentials.credentials
            )
            user_attributes = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}

            # MySQL에서 사용자 권한 조회
            query = "SELECT permission FROM user_role WHERE cognito_username = %s"
            permission_result = await MySQLConnector.fetch_one(query, (response['Username'],))
            permission = permission_result['permission'] if permission_result else 0

            return {
                "username": response['Username'],
                "email": user_attributes.get('email'),
                "permission": permission
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid token")


async def is_admin(user: dict = Depends(get_current_user)):
    if user['permission'] != 1:  # 1은 관리자 권한
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/request-signup")
async def request_signup(user: UserRequest):
    query = """INSERT INTO cognito_signup_request 
               (email, username, status) 
               VALUES (%s, %s, %s)"""
    values = (user.email, user.username, 1)  # 1 for pending status
    request_id = await MySQLConnector.execute_query(query, values)
    return {"message": "Signup request submitted", "request_id": request_id}


@router.get("/pending-requests", dependencies=[Depends(is_admin)])
async def get_pending_requests():
    query = "SELECT * FROM cognito_signup_request WHERE status = 1"
    result = await MySQLConnector.fetch_all(query)
    return result


@router.post("/approve-signup/{request_id}")
async def approve_signup(request_id: int, admin: dict = Depends(is_admin)):
    query = "SELECT * FROM cognito_signup_request WHERE request_id = %s AND status = 1"
    user = await MySQLConnector.fetch_one(query, (request_id,))

    if not user:
        raise HTTPException(status_code=404, detail="Request not found or already processed")

    async with aioboto3.Session().client('cognito-idp', region_name=settings.aws_region) as cognito:
        try:
            response = await cognito.admin_create_user(
                UserPoolId=settings.cognito_user_pool_id,
                Username=user["username"],
                UserAttributes=[
                    {'Name': 'email', 'Value': user["email"]},
                    {'Name': 'email_verified', 'Value': 'true'}
                ],
                TemporaryPassword='TemporaryPass123!',
                MessageAction='SUPPRESS'
            )

            # 사용자 비밀번호 설정
            await cognito.admin_set_user_password(
                UserPoolId=settings.cognito_user_pool_id,
                Username=user["username"],
                Password=user["password"],
                Permanent=True
            )

            # MySQL에 사용자 권한 추가
            role_query = "INSERT INTO user_role (email, cognito_username, permission) VALUES (%s, %s, %s)"
            await MySQLConnector.execute_query(role_query, (user["email"], user["username"], 2))  # 2는 뷰어 권한

        except cognito.exceptions.UsernameExistsException:
            raise HTTPException(status_code=400, detail="User already exists in Cognito")

    update_query = """UPDATE cognito_signup_request 
                      SET status = 2, approved_by = %s, approved_at = NOW() 
                      WHERE request_id = %s"""
    await MySQLConnector.execute_query(update_query, (admin['username'], request_id))

    return {"message": "User approved and created", "username": response['User']['Username']}


@router.post("/login")
async def login(user: LoginUser):
    async with aioboto3.Session().client('cognito-idp', region_name=settings.aws_region) as cognito:
        try:
            response = await cognito.initiate_auth(
                ClientId=settings.cognito_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': user.username,
                    'PASSWORD': user.password
                }
            )
            return {
                "message": "Login successful",
                "token": response['AuthenticationResult']['AccessToken'],
                "id_token": response['AuthenticationResult']['IdToken']
            }
        except cognito.exceptions.NotAuthorizedException:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-info")
async def get_user_info(user: dict = Depends(get_current_user)):
    return user


@router.post("/set-permission/{username}")
async def set_permission(username: str, permission: int, admin: dict = Depends(is_admin)):
    if permission not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="Invalid permission level")

    query = "UPDATE user_role SET permission = %s WHERE cognito_username = %s"
    result = await MySQLConnector.execute_query(query, (permission, username))
    if result == 0:
        raise HTTPException(status_code=404, detail="User not found")

    permission_names = {0: "no permission", 1: "admin", 2: "viewer"}
    return {"message": f"User {username} has been set as {permission_names[permission]}"}