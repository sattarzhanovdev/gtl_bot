import hmac, hashlib, time, json, base64
from django.conf import settings
import jwt

BOT_TOKEN = settings.BOT_TOKEN
JWT_SECRET = settings.JWT_SECRET
JWT_TTL_SECONDS = settings.JWT_TTL_SECONDS


def verify_webapp_init_data(init_data: str) -> dict:
    # init_data: "query_id=...&user=...&auth_date=...&hash=..."
    from urllib.parse import parse_qsl
    params = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = params.pop("hash", "")
    data_check_string = "\n".join(f"{k}={params[k]}" for k in sorted(params.keys()))
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    calc_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calc_hash, received_hash):
        raise ValueError("Bad signature")
    return params


def create_jwt(payload: dict) -> str:
    payload = {**payload, "iat": int(time.time()), "exp": int(time.time()) + JWT_TTL_SECONDS}
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_jwt(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])