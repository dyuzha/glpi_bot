from .mail import mail_confirmation
from .db import DBInterface

# from .ad import get_email
from .ad import LDAPService

from .async_ad import AsyncLDAPService
from config_handlers import AD_CONFIG
from typing import Optional, Union


def get_email(login):
    with LDAPService(AD_CONFIG) as ldap_conn:
        email = ldap_conn.get_user_mail(login, base_dn="dc=krd")
        return email

# async def get_email(login: str) -> Union[str, bool]:
#     try:
#         async with AsyncLDAPService(AD_CONFIG) as ldap:
#             email = await ldap.get_user_mail(login, base_dn="dc=krd")
#             return email
#     except Exception as e:
#         # Логируем ошибку и пробрасываем дальше
#         raise RuntimeError(f"Failed to get email for {login}: {str(e)}") from e
