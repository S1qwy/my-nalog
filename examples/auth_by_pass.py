"""
Пример авторизации по ИНН и паролю
"""

from my_nalog import NalogRuAPI

client = NalogRuAPI()

if client.is_authenticated():
    print("Уже авторизован!")
else:
    inn = input("Введите ИНН (10 или 12 цифр): ")
    password = input("Введите пароль: ")
    
    try:
        profile = client.auth_by_password(inn, password)
        print(f"Авторизация успешна! Добро пожаловать, {profile.name}")
        print(f"ИНН: {profile.inn}, Телефон: {profile.phone}")
    except Exception as e:
        print(f"Ошибка авторизации: {str(e)}")
