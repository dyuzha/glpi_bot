from app.config_handlers import GLPI_CONFIG
from app.glpi import GLPIConnection, GLPIService

# login = "dyuzhev_mn"
login = "tgbot"

with GLPIConnection(**GLPI_CONFIG) as glpi:
    glpi_service = GLPIService(glpi)
    glpi_user = glpi_service.get_user(login)

print(glpi_user.get_id())



ticket_data = {
    "input": {
        "name": "test_name",
        "content": "test_cont",
        "type": "1", # 1 для инцидента, 2 для запроса
        # "urgency": 3, # Срочность (1-5)
        # "impact": 3, # Влияние (1-5)
        # "priority": 3, # Приоритет (1-5)
        "requesttypes_id": 2, # Источник запроса
        # "itilcategories_id": 1, ID Категории,
        "_users_id_requester": 291, # ID пользователя-заявителя
        "entities_id": 10  # ID организации (0 для корневой)
    }
}





# Создаем заявку в GLPI
with GLPIConnection(**GLPI_CONFIG) as glpi:
    result = glpi.make_request("POST", "Ticket", json_data=ticket_data)
    print(result)

"""
{
    'totalcount': 2,
    'count': 2,
    'sort': ['1'],
    'order': ['ASC'],
        'data': [
            {
                '1': 'dyakonenko_da',
                '77': 'Техническая поддержка',
                '34': 'Дьяконенко Дарья Александровна',
                '9': None,
                '5': 'dyakonenko_da@art-t.ru',
                '6': '',
                '3': 'Проф ИТ',
                '8': 1,
                '20': 'Self-Service'
            },
            {
                '1': 'dyuzhev_mn',
                '77': 'Техническая поддержка',
                '34': 'Дюжев Матвей Николаевич',
                '9': 'Матвей Николаевич',
                '5': 'dyuzhev_mn@it4prof.ru',
                '6': '',
                '3': 'Проф ИТ',
                '8': 1,
                '20': 'Super-Admin'}
            ],
        'content-range': '0-1/2'}
"""

