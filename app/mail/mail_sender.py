import aiosmtplib
from email.mime.text import MIMEText
import random
import string
from config_handlers import MAIL_DATA
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MailSender():
    """Класс для отправки сообщений на email"""
    def __init__(self, mail_config):
        self.smtp_server = mail_config['smtp_server']
        self.smtp_port = mail_config['smtp_port']
        self.smtp_username = mail_config['smtp_username']
        self.smtp_password = mail_config['smtp_password']
        self.use_tls = mail_config['use_tls']

    def generate_confirmation_code(self, length=8) -> str:
        """Генерация случайного кода подтверждения"""
        characters = string.digits  # Используем только цифры
        return ''.join(random.choice(characters) for _ in range(length))

    def _build_confirm_mail(self, code: str, email_to: str) -> MIMEText:
        """Создание email сообщения"""
        subject = "Код подтверждения авторизации в Telegram-боте **ПРОФИТ**"
        body = f"""Здравствуйте,\n
        Ваш код подтверждения для телеграмм-бота: {code}\n
        Введите этот код в сообщениях боту для регистрации.
        """
        # Создание сообщения
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.smtp_username
        msg['To'] = email_to
        return msg

    async def send_confirmation_email(self, email_to: str) -> Optional[str]:
        """Асинхронная отправка письма с кодом подтверждения"""
        code = self.generate_confirmation_code()
        msg = self._build_confirm_mail(code, email_to)

        try:
            # Подключение и отправка
            async with aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=self.use_tls
            ) as server:
                await server.login(self.smtp_username, self.smtp_password)
                await server.send_message(msg)

            logger.info(f"Письмо с кодом подтверждения успешно отправлено \
                    на {msg['To']}")
            return code
        except Exception as e:
            logger.warning(f"Ошибка при отправке письма на {msg['To']}: {e}")
            return None

mail_sender = MailSender(MAIL_DATA)
