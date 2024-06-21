import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings

SMTP_SERVER = settings.smtp_server
SMTP_PORT = settings.smtp_port
SMTP_USERNAME = settings.smtp_username
SMTP_PASSWORD = settings.smtp_password
FROM_EMAIL = SMTP_USERNAME  # 발신 이메일 주소는 SMTP 사용자 이름과 동일합니다.


def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # TLS 모드로 서버 연결
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
