"""
Базовый пример работы с библиотекой my-nalog:
- Авторизация по SMS
- Создание чека
"""

from my_nalog import NalogRuAPI

client = NalogRuAPI()

if client.is_authenticated():
    print("Уже авторизован по сохраненной сессии")
else:
    phone = input("Введите номер телефона (11 цифр): ")
    
    client.auth_by_sms(phone)
    print("SMS отправлено, ожидайте код...")
    
    sms_code = input("Введите код из SMS (6 цифр): ")
    
    profile = client.verify_sms(sms_code, client.last_challenge_token)
    print(f"Авторизация успешна! ИНН: {profile.inn}")

amount = float(input("Введите сумму чека: "))
description = input("Введите описание чека: ")

receipt = client.create_receipt(amount, description)
print(f"Чек создан! Ссылка для печати: {receipt.link}")
