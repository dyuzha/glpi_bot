from app.config_handlers import GLPI_CONFIG
from app.glpi import GLPIConnection

login = "dyuzhev_mn"

data = {
    "searchText": f"[{login}]",
    "searchOption": "1"
}

with GLPIConnection(**GLPI_CONFIG) as glpi:
    result = glpi.make_request("POST", "User", json_data=data)
    print(result)

