# my-nalog

<img src="https://img.shields.io/pypi/v/my-nalog?style=flat-square" alt="PyPI version"> 
<img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">

Python клиент для работы с API сервиса "Мой Налог" (lknpd.nalog.ru)

## 🔥 Возможности

- ✅ Авторизация по SMS или логину/паролю
- 🧾 Создание чеков (приходных ордеров)
- 🔗 Получение ссылки на печатную форму чека
- 💾 Сохранение сессии между запусками
- 🛠 Обработка ошибок API

## 📦 Установка

```bash
pip install my-nalog
```

## 🚀 Быстрый старт

### Авторизация по SMS

```python
from my_nalog import NalogRuAPI

api = NalogRuAPI()

# Запрос SMS с кодом подтверждения
sms_response = api.auth_by_sms("79991234567")  # Номер телефона

# Подтверждение кода из SMS
user_profile = api.verify_sms("123456", sms_response['challengeToken'])

print(f"Авторизован как: {user_profile.name}")
```

### Авторизация по паролю

```python
from my_nalog import NalogRuAPI

api = NalogRuAPI()

# Авторизация по ИНН и паролю
user_profile = api.auth_by_password("123456789012", "my_password")

print(f"Авторизован как: {user_profile.name}")
```

### Cоздание чека

```python
# Создание чека на сумму 100.50 рублей
receipt = api.create_receipt(100.50, "Консультационные услуги")

print(f"Чек создан: {receipt.uuid}")
print(f"Ссылка на чек: {receipt.link}")
```

## 📚 Документация

### Класс NalogRuAPI

##### Основной класс для работы с API.

#### Методы авторизации:

**auth_by_sms(phone: str) -> dict** - запрос SMS с кодом подтверждения

**verify_sms(code: str, challenge_token: str)** -> UserProfile - подтверждение кода из SMS

**auth_by_password(inn: str, password: str) -> UserProfile** - авторизация по ИНН и паролю

**logout()** - завершение сессии

#### Работа с чеками:

**create_receipt(amount: float, description: str) -> Receipt** - создание чека

**get_receipt_link(receipt_uuid: str) -> str** - получение ссылки на чек

#### Дополнительные методы:

**is_authenticated() -> bool** - проверка авторизации

**_save_session()** - сохранение сессии (используется автоматически)

**_load_session()** - загрузка сессии (используется автоматически)

### Модели данных

#### UserProfile

**inn: str** - ИНН пользователя

**phone: str** - телефон

**name: str** - имя

**email: Optional[str]** - email

**snils: Optional[str]** - СНИЛС

#### Receipt

**uuid: str** - идентификатор чека

**amount: float** - сумма

**description: str** - описание

**created_at: datetime** - дата создания

**link: str** - ссылка на печатную форму

### ⚠️ Обработка ошибок

#### Библиотека определяет следующие исключения:

**AuthError** - ошибки авторизации

**SmsError** - ошибки при работе с SMS

**ReceiptError** - ошибки при работе с чеками

**SessionError** - ошибки работы с сессией

**NalogAPIError** - общие ошибки API

### 👨‍💻 Разработка

#### Клонируйте репозиторий:

```bash
git clone https://github.com/ваш-репозиторий/my-nalog.git
cd my-nalog
```

#### Установите зависимости:

```bash
pip install -e .
```

#### Запустите тесты:

```bash
pytest
```

### 🤝 Участие в проекте
#### Приветствуются pull requests! Для крупных изменений сначала откройте issue, чтобы обсудить, что вы хотите изменить.

### 📜 Лицензия
#### Этот проект распространяется под лицензией MIT. Подробнее см. в файле LICENSE.
