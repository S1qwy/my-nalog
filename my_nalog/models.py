from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Receipt:
    uuid: str
    amount: float
    description: str
    created_at: datetime
    link: str

@dataclass
class UserProfile:
    inn: str
    phone: str
    name: str
    email: Optional[str] = None
    snils: Optional[str] = None
