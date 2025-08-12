class NalogAPIError(Exception):
    pass

class AuthError(NalogAPIError):
    pass

class SmsError(NalogAPIError):
    pass

class ReceiptError(NalogAPIError):
    pass

class SessionError(NalogAPIError):
    pass
