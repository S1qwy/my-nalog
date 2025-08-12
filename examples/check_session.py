"""
Пример проверки сохраненной сессии
"""

from my_nalog import NalogRuAPI

client = NalogRuAPI()

if client.is_authenticated():
    print("Сессия активна!")
    print(f"ИНН: {client.inn}")
    print(f"Телефон: {client.phone}")
else:
    print("Нет активной сессии. Требуется авторизация.")
