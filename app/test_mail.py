from services import mail_confirmation
import asyncio


async def send_email():
    code = await mail_confirmation.send_confirmation_email("matvey10d@gmail.com")
    if code:
        print(f"Письмо отправлено! Код подтверждения: {code}")
    else:
        print("Ошибка отправки письма!")

asyncio.run(send_email())
