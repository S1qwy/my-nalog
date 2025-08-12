"""
Пример создания нескольких чеков в цикле
"""

from my_nalog import NalogRuAPI
from time import sleep

client = NalogRuAPI()

if not client.is_authenticated():
    print("Сначала нужно авторизоваться!")
    exit()

receipts_data = [
    {"amount": 100.50, "description": "Консультационные услуги"},
    {"amount": 250.00, "description": "Разработка сайта"},
    {"amount": 500.75, "description": "Дизайн интерфейса"}
]

for item in receipts_data:
    try:
        receipt = client.create_receipt(item["amount"], item["description"])
        print(f"Чек на {item['amount']} руб. создан: {receipt.link}")
        sleep(1)
    except Exception as e:
        print(f"Ошибка при создании чека: {str(e)}")
