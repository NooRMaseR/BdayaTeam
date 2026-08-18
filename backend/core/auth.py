from core.permissions import JWTCookiesAuthentication
from utils import STORE

JWT_COOKIES_AUTH = JWTCookiesAuthentication(cookie="access_token")
