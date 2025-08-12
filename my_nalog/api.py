import requests
import json
import pickle
import os
import random
import string
from datetime import datetime, timezone
from typing import Dict, Optional, Union
from .exceptions import AuthError, SmsError, ReceiptError, SessionError, NalogAPIError
from .models import Receipt, UserProfile


class NalogRuAPI:
    SESSION_FILE = "nalog_session.pkl"
    BASE_URL = "https://lknpd.nalog.ru/api/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.refresh_token = None
        self.phone = None
        self.inn = None
        self.device_id = self._generate_device_id()
        self._load_session()
        self.last_challenge_token = None

    # ======================
    # Intenal methods
    # ======================
    
    def _generate_device_id(self, length=32) -> str:
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def _get_device_info(self) -> Dict:
        return {
            "appVersion": "1.0.0",
            "sourceDeviceId": self.device_id,
            "sourceType": "WEB",
            "metaDetails": {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "browser": "Chrome",
                "browserVersion": "91.0.4472.124",
                "os": "Windows"
            }
        }

    def _save_session(self):
        try:
            session_data = {
                'token': self.token,
                'refresh_token': self.refresh_token,
                'phone': self.phone,
                'inn': self.inn,
                'device_id': self.device_id,
                'cookies': requests.utils.dict_from_cookiejar(self.session.cookies)
            }
            with open(self.SESSION_FILE, 'wb') as f:
                pickle.dump(session_data, f)
        except Exception as e:
            raise SessionError(f"Ошибка сохранения сессии: {str(e)}")

    def _load_session(self):
        if not os.path.exists(self.SESSION_FILE):
            return
            
        try:
            with open(self.SESSION_FILE, 'rb') as f:
                data = pickle.load(f)
            
            self.token = data.get('token')
            self.refresh_token = data.get('refresh_token')
            self.phone = data.get('phone')
            self.inn = data.get('inn')
            self.device_id = data.get('device_id', self._generate_device_id())
            
            if cookies := data.get('cookies'):
                self.session.cookies = requests.utils.cookiejar_from_dict(cookies)
        except Exception as e:
            raise SessionError(f"Ошибка загрузки сессии: {str(e)}")

    def _make_request(self, endpoint: str, data: Optional[Dict] = None) -> Dict:
        try:
            url = f"{self.BASE_URL}{endpoint}"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            
            request_data = {
                "deviceInfo": self._get_device_info(),
                **(data if data else {})
            }


            response = self.session.post(
                url,
                json=request_data,
                headers=headers,
                timeout=30
            )


            if response.status_code != 200:
                try:
                    error_msg = response.json().get('message', f"HTTP {response.status_code}")
                except json.JSONDecodeError:
                    error_msg = f"HTTP {response.status_code} - Не удалось декодировать JSON"

                if response.status_code == 401:
                    raise AuthError(error_msg)
                elif response.status_code == 422:
                    raise SmsError(error_msg)
                else:
                    raise NalogAPIError(error_msg)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise NalogAPIError(f"Ошибка сети: {str(e)}")
        except json.JSONDecodeError:
            raise NalogAPIError("Неверный формат ответа от сервера")

    # ======================
    # Authorization methods
    # ======================
    
    def auth_by_sms(self, phone: str) -> None:
        if len(phone) != 11 or not phone.isdigit():
            raise SmsError("Номер должен содержать 11 цифр")
        
        self.phone = phone
        response = self._make_request("/auth/challenge/sms/start", {"phone": phone})

        if not response.get('challengeToken'):
            raise SmsError("Не удалось отправить SMS")

        self.last_challenge_token = response.get('challengeToken')

    
    def verify_sms(self, sms_code: str, challenge_token: str) -> UserProfile:
        if len(sms_code) != 6 or not sms_code.isdigit():
            raise SmsError("Код должен содержать 6 цифр")
        
        response = self._make_request("/auth/challenge/sms/verify", {
            "phone": self.phone,
            "challengeToken": challenge_token,
            "code": sms_code
        })
        
        if not response.get('token'):
            raise AuthError("Неверный код подтверждения")
        
        self.token = response['token']
        self.refresh_token = response.get('refreshToken')
        self.inn = response.get('profile', {}).get('inn')
        self._save_session()
        
        return self._parse_profile(response.get('profile', {}))

    def auth_by_password(self, inn: str, password: str) -> UserProfile:
        if len(inn) not in (10, 12) or not inn.isdigit():
            raise AuthError("ИНН должен содержать 10 или 12 цифр")
        
        response = self._make_request("/auth/signin", {
            "inn": inn,
            "password": password
        })
        
        if not response.get('token'):
            raise AuthError("Неверные учетные данные")
        
        self.token = response['token']
        self.refresh_token = response.get('refreshToken')
        self.inn = inn
        self._save_session()
        
        return self._parse_profile(response.get('profile', {}))

    def _parse_profile(self, profile_data: Dict) -> UserProfile:
        return UserProfile(
            inn=profile_data.get('inn', ''),
            phone=profile_data.get('phone', ''),
            name=profile_data.get('displayName', ''),
            email=profile_data.get('email'),
            snils=profile_data.get('snils')
        )

    # ======================
    # Income methods
    # ======================
    
    def create_receipt(self, amount: float, description: str) -> Receipt:
        if not self.token:
            raise AuthError("Требуется авторизация")
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ReceiptError("Сумма должна быть положительной")
        except ValueError:
            raise ReceiptError("Неверный формат суммы")
    
        now = datetime.now(timezone.utc)
        operation_time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        request_time = now.isoformat()
    
        receipt_data = {
            "amount": amount,
            "name": description,
            "quantity": 1,
            "operationTime": operation_time,
            "requestTime": request_time,
            "paymentType": "WIRE",
            "client": {
                "incomeType": "FROM_INDIVIDUAL",
                "contactPhone": self.phone or "",
                "displayName": "Клиент"
            },
            "services": [
                {
                    "name": description,
                    "quantity": 1,
                    "amount": amount,
                    "price": amount
                }
            ],
            "totalAmount": amount,
            "ignoreMaxTotalIncomeRestriction": False
        }
    

        
        try:
            response = self._make_request("/income", receipt_data)
        except NalogAPIError as e:
            raise ReceiptError(f"Не удалось создать чек: {str(e)}")
    
        if not response.get('approvedReceiptUuid'):
            raise ReceiptError("Не удалось создать чек: не получен UUID чека")
    
        return Receipt(
            uuid=response['approvedReceiptUuid'],
            amount=amount,
            description=description,
            created_at=now,
            link=self.get_receipt_link(response['approvedReceiptUuid'])
        )
    
    def get_receipt_link(self, receipt_uuid: str) -> str:
        if not self.inn:
            raise ReceiptError("ИНН не найден")
        
        return f"https://lknpd.nalog.ru/api/v1/receipt/{self.inn}/{receipt_uuid}/print"

    # ======================
    # Auxiliary methods
    # ======================
    
    def is_authenticated(self) -> bool:
        return bool(self.token)
    
    def logout(self):
        self.token = None
        self.refresh_token = None
        self.phone = None
        self.inn = None
        self.session.cookies.clear()
        if os.path.exists(self.SESSION_FILE):
            os.remove(self.SESSION_FILE)
