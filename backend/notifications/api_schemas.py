from ninja import Schema

class SubscriptionRequest(Schema):
    endpoint: str
    auth: str
    p256dh: str

class UnsubscribeRequest(Schema):
    endpoint: str
