import hmac, hashlib, time, json, base64
from django.conf import settings
import jwt, urllib

BOT_TOKEN = settings.BOT_TOKEN
JWT_SECRET = settings.JWT_SECRET
JWT_TTL_SECONDS = settings.JWT_TTL_SECONDS


def verify_webapp_init_data(init_data: str) -> dict:
    """Проверка подписи initData из Telegram WebApp"""
    params = dict(urllib.parse.parse_qsl(init_data or ""))
    hash_recv = params.pop("hash", None)
    if not hash_recv:
        raise ValueError("hash missing")

    # Строка для проверки
    check_str = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hash_calc = hmac.new(secret, check_str.encode(), hashlib.sha256).hexdigest()
    if hash_recv != hash_calc:
        raise ValueError("bad signature")
    return params

def create_jwt(payload: dict) -> str:
    now = int(time.time())
    payload = {"iat": now, "exp": now + 7*24*3600, **payload}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])