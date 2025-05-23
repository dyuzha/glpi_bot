class LDAPError(Exception):
    """Класс для ошибок взаимодействия с LDAP"""
    def __str__(self):
        return "Ошибка при получении данных из LDAP"


class LDAPUserNotFound(ValueError):
    def __str__(self):
        return "Пользователь не найден"


class LDAPMailNotFound(ValueError):
    def __str__(self):
        return "Mail не найден у данного пользователя"

