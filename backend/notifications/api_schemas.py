import msgspec

class SubscriptionRequestMSG(msgspec.Struct):
    endpoint: str
    auth: str
    p256dh: str

class UnsubscribeRequestMSG(msgspec.Struct):
    endpoint: str
