import smtplib
from email.mime.text import MIMEText
import random
import string
from config_handlers import MAIL_DATA
import logging

logger = logging.getLogger(__name__)

class MailSender():
    """Класс для отправки сообщений на email"""
    def __init__(self, mail_config):
        self.smtp_server = mail_config['smtp_server']
        self.smtp_port = mail_config['smtp_port']
        self.smtp_username = mail_config['smtp_username']
        self.smtp_password = mail_config['smtp_password']

    def generate_confirmation_code(self, length=8) -> str:
        """Генерация случайного кода подтверждения"""
        characters = string.digits  # Используем только цифры
        return ''.join(random.choice(characters) for _ in range(length))

    def build_confirm_mail(self, code, email_to) -> None:
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

    def send_confirmation_email(self, msg: MIMEText) -> bool:
        """Отправка письма с кодом подтверждения"""
        try:
            # Подключение и отправка
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            logger.info(f"Письмо с кодом подтверждения успешно отправлено \
                    на {msg['To']}")
            return True
        except Exception as e:
            logger.warning(f"Ошибка при отправке письма на {msg['To']}: {e}")
            return False

mail_sender = MailSender(MAIL_DATA)
