import asyncio
from typing import Optional, Union
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException


class AsyncLDAPService:
    def __init__(self, config):
        self.config = config
        self.connection: Optional[Connection] = None

    async def __aenter__(self):
        try:
            # Выносим блокирующие операции в отдельный поток
            server = await asyncio.to_thread(
                Server,
                self.config.LDAP_SERVER_URL,
                get_info=ALL
            )

            self.connection = await asyncio.to_thread(
                Connection,
                server,
                user=self.config.get_admin_login(),
                password=self.config.get_admin_password(),
                auto_bind=True
            )
            return self
        except LDAPException as e:
            raise ConnectionError(f"LDAP connection failed: {str(e)}") from e

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.connection and not self.connection.closed:
            await asyncio.to_thread(self.connection.unbind)

    async def get_user_mail(self, username: str, base_dn: str) -> Union[str, bool]:
        """Асинхронно получает email пользователя из AD"""
        if not self.connection or self.connection.closed:
            raise RuntimeError("LDAP connection is not established")

        try:
            search_filter = f"(sAMAccountName={username})"

            # Выполняем поиск в отдельном потоке
            await asyncio.to_thread(
                self.connection.search,
                search_base=base_dn,
                search_filter=search_filter,
                attributes=['mail']
            )

            if not self.connection.entries:
                return False

            user_entry = self.connection.entries[0]
            if 'mail' not in user_entry or not user_entry.mail.value:
                raise ValueError(f"User {username} has no email in AD")

            return str(user_entry.mail.value)
        except LDAPException as e:
            raise RuntimeError(f"LDAP error: {str(e)}") from e


