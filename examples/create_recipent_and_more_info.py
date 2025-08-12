"""
Пример создания чека и получения максимальной информации о нем
"""

from my_nalog import NalogRuAPI

client = NalogRuAPI()

if not client.is_authenticated():
    print("Сначала авторизуйтесь!")
    exit()

# Создаем тестовый чек
receipt = client.create_receipt(300, "Пример чека")

# Получаем ссылку на печать
print(f"ID чека: {receipt.uuid}")
print(f"Ссылка для печати: {receipt.link}")
print(f"Дата создания: {receipt.created_at}")
