from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import config
from src.services.auth import auth_service


class EmailService:
    conf = ConnectionConfig(
        MAIL_USERNAME=config.MAIL_USERNAME,
        MAIL_PASSWORD=config.MAIL_PASSWORD,
        MAIL_FROM=config.MAIL_FROM,
        MAIL_PORT=config.MAIL_PORT,
        MAIL_SERVER=config.MAIL_SERVER,
        MAIL_FROM_NAME="FastContacts",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=config.BASE_DIR / "src" / "services" / "templates",
    )
    fm = FastMail(conf)

    async def send_varification_mail(self, email: EmailStr, username: str, host: str):
        try:
            token_verification = auth_service.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Confirm your email",
                recipients=[email],
                template_body={
                    "host": host,
                    "username": username,
                    "token": token_verification,
                },
                subtype=MessageType.html,
            )
            await self.fm.send_message(message, template_name="verify_email.html")

        except ConnectionErrors as err:
            print(err)

    async def send_request_password_mail(
        self, email: EmailStr, username: str, host: str
    ):
        try:
            token_verification = auth_service.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Request psw",
                recipients=[email],
                template_body={
                    "host": host,
                    "username": username,
                    "token": token_verification,
                },
                subtype=MessageType.html,
            )
            await self.fm.send_message(
                message, template_name="request_password_reset.html"
            )

        except ConnectionErrors as err:
            print(err)

    async def send_new_password_mail(
        self, email: EmailStr, username: str, new_password: str,
    ):
        try:
            message = MessageSchema(
                subject="New psw",
                recipients=[email],
                template_body={
                    "username": username,
                    "new_psw": new_password,
                },
                subtype=MessageType.html,
            )
            await self.fm.send_message(message, template_name="new_password.html")

        except ConnectionErrors as err:
            print(err)
