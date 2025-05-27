import aiosmtplib
import ssl
from email.mime.text import MIMEText
import random
import string
from typing import Optional
import logging
# import certifi


logger = logging.getLogger(__name__)

MAIL_SUBJECT = "Код подтверждения авторизации в Telegram-боте ПРОФИТ"
MAIL_BODY = (
    "Здравствуйте,\n"
    "Ваш код подтверждения для телеграмм-бота: {}\n"
    "Введите этот код в сообщениях боту для регистрации."
)


class EmailConfirmation():
    """Класс для подтверждения email"""
    subject = MAIL_SUBJECT or "Код подтверждения авторизации в Telegram-боте ПРОФИТ"
    body = MAIL_BODY or """
        Здравствуйте,\n
        Ваш код подтверждения для телеграмм-бота: {}\n
        Введите этот код в сообщениях боту для регистрации.
        """

    def __init__(self, **mail_data):
        self.smtp_server = mail_data['smtp_server']
        self.smtp_port = mail_data['smtp_port']
        self.smtp_username = mail_data['smtp_username']
        self.smtp_password = mail_data['smtp_password']
        self.use_tls = mail_data['use_tls']

    def generate_confirmation_code(self, length=4) -> str:
        """Генерация случайного кода подтверждения"""
        characters = string.digits  # Используем только цифры
        return ''.join(random.choice(characters) for _ in range(length))

    def _build_confirm_mail(self, code: str, email_to: str) -> MIMEText:
        """Создание email сообщения"""
        msg = MIMEText(self.body.format(code))
        msg['Subject'] = self.subject
        msg['From'] = self.smtp_username
        msg['To'] = email_to
        return msg

    async def send_confirmation_email(self, email_to: str, length=4) -> Optional[str]:
        """Асинхронная отправка письма с кодом подтверждения"""
        code = self.generate_confirmation_code(length=length)
        logger.debug(f"Сгенерирован код подтверждения: <{code}>")
        msg = self._build_confirm_mail(code, email_to)
        logger.debug(f"Собранно письмо для отправки:")


        # Настройка SSL контекста
        context = ssl.create_default_context()
        # try:
        # Пытаемся использовать системные сертификаты
        context.load_default_certs()
        # except:
        #     # Fallback на certifi если системные недоступны
        #     context = ssl.create_default_context(cafile=certifi.where())
        #
        # Выключает проверку TLS (Для тестов, если на хосте нет корневых certs)
        # context = ssl._create_unverified_context()

        try:
            logger.debug("Подключение к SMTP серверу")
            # Подключение и отправка
            async with aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=self.use_tls,
                tls_context=context,
            ) as server:
                try:
                    await server.login(self.smtp_username, self.smtp_password)
                    logger.debug("Успешная авторизация на SMTP сервере")
                except Exception as e:
                    logger.warning("Неудачная авторизация на SMTP сервере")

                await server.send_message(msg)

            logger.info(f"Письмо с кодом подтверждения успешно отправлено \
                    на {msg['To']}")
            return code
        except Exception as e:
            logger.warning(f"Ошибка при отправке письма на {msg['To']}: {e}")
            return None
