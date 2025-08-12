"""
Пример обработки различных ошибок API
"""

from my_nalog import NalogRuAPI
from my_nalog.exceptions import AuthError, SmsError, ReceiptError

client = NalogRuAPI()

try:
    if not client.is_authenticated():
        receipt = client.create_receipt(100, "Тест")
except AuthError as e:
    print(f"Ошибка авторизации: {str(e)}")
except ReceiptError as e:
    print(f"Ошибка чека: {str(e)}")

try:
    client.auth_by_sms("123")
except SmsError as e:
    print(f"Ошибка SMS: {str(e)}")
