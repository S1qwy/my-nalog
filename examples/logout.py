"""
Пример выхода из системы (logout)
"""

from my_nalog import NalogRuAPI

client = NalogRuAPI()

if client.is_authenticated():
    print("Выполняю выход из системы...")
    client.logout()
    print("Успешно вышли из системы!")
else:
    print("Нет активной сессии для выхода.")
