"""
Головний системний файл views для виклику конекторів та виведення результатів на сторінки
"""
from modules.trembita.configs.trembita_config import trembita_headers, trembita_url
from modules.trembita.connectors.request_codes import country_code

def country(request):
    """функція використання конектора country_code
    params: us - for counrty code
    settings: default
    """
    return country_code('us', trembita_url, trembita_headers)


