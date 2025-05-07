import logging
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException
from typing import Optional, Type
from types import TracebackType

logger = logging.getLogger(__name__)


class LDAPService:
    def __init__(self, config):
        self.config = config
        self.connection: Optional[Connection] = None

    def __enter__(self):
        try:
            self.connection = Connection(
                server= self.config.server,
                user=self.config.user,
                password=self.config.password,
                auto_bind=True
            )
            logger.error(f"Подключение к ldap осуществлено!")
            return self
        except LDAPException as e:
            logger.error(f"Connection error: {e}")
            raise

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> bool:
        if self.connection:
            if not self.connection.closed:
                self.connection.unbind()

        return exception_type is None


    def get_user_mail(self, username, base_dn) -> bool | str:

        if not self.connection or self.connection.closed:
            raise RuntimeError("LDAP connection is not established")

        try:
             # Ищем пользователя по sAMAccountName
            search_filter = f"(sAMAccountName={username})"
            logger.info(f"Поиск пользователя по логину: {username}")
            self.connection.search(
                search_base=base_dn,
                search_filter=search_filter,
                attributes=['mail']
            )

            if not self.connection.entries:
                logger.info(f"Пользователь {username} не найден:")
                return False  # Пользователь не найден

            user_entry = self.connection.entries[0]
            logger.info(f"Найден пользователь: {user_entry}")

            if 'mail' not in user_entry or not user_entry.mail.value:
                raise ValueError(f"У пользователя {username} не указан email в AD")

            return str(user_entry.mail.value)

        except LDAPException as e:
            logger.error(f"LDAP error: {e}")
            return False

